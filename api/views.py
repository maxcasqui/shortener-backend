from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import ValidationError
from django.http import Http404,HttpResponseRedirect
from .models import URL
from .validations import validate_data, validate_url_logged_user, validate_url_notlogged_user
from .serializers import AllURLSerializer, NotAuthenticatedURLSerializer, UserRegisterSerializer, UserLoginSerializer, UserSerializer, URLSerializer, RedirectSerializer

class UserRegister(APIView):
    permission_classes = (permissions.AllowAny,)
    ##
    def post(self, request):
        try:
            clean_data = validate_data(request.data)
            serializer = UserRegisterSerializer(data=clean_data)
            ##
            if serializer.is_valid(raise_exception=True):
                user = serializer.create(clean_data)
                if user:
                    return Response({'detail': 'User Created.'}, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({'detail': e.detail[0]}, status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
    permission_classes = (permissions.AllowAny,)
    ##
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            tokens_data = {
                'access_token': serializer.validated_data['access'],
                'refresh_token': serializer.validated_data['refresh'],
                }
            return Response(tokens_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogout(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        token = request.data.get('refresh_token')
        ##
        if token:
            try:
                refresh_token = RefreshToken(token)
                refresh_token.blacklist()
                return Response({'detail': 'Logout successful.'}, status=status.HTTP_200_OK)
            except TokenError as te:
                return Response({'detail': str(te)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Token Invalid or Expired.'}, status=status.HTTP_200_OK)

class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    ##
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)

class UrlView(APIView):
    # permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        try:
            url = URL.objects.get(id=id)
            serializer = URLSerializer(url)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        if request.user.is_authenticated:
            try:
                clean_data = validate_url_logged_user(request.data)
                serializer = URLSerializer(data=clean_data, context={'request': request})
                if serializer.is_valid():
                    instance = serializer.save()
                    return Response({'slug': instance.slug}, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except ValidationError as e:
                return Response({'error': e.detail[0]}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If not authenticated, only original_url must be send
            try:
                clean_data = validate_url_notlogged_user(request.data)
                serializer = NotAuthenticatedURLSerializer(data=clean_data)

                if serializer.is_valid():
                    instance = serializer.save()
                    return Response({'slug': instance.slug}, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except ValidationError as e:
                return Response({'error': e.detail[0]}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        if not request.user.is_authenticated:
            return Response({'message':'User must be logged'}, status=status.HTTP_403_FORBIDDEN)
        try:
            url = URL.objects.get(id=id)
            user = request.user
            if url.user != user:
                return Response({'message':'This resource can only be updated by the owner'}, status=status.HTTP_403_FORBIDDEN)

            clean_data = validate_url_logged_user(request.data)
            serializer = URLSerializer(instance=url, data=clean_data, context={'request': request})
            if serializer.is_valid():
                instance = serializer.save()
                return Response({'id':instance.id ,'url': instance.original_url, 'slug': instance.slug}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({'error': e.detail[0]}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('Exception e')
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, id):
        if not request.user.is_authenticated:
            return Response({'message':'User must be logged'}, status=status.HTTP_403_FORBIDDEN)

        try:
            found_url = URL.objects.get(id=id)
            user = request.user
            if found_url.user != user:
                return Response({'message':'This resource can only be deleted by the owner'}, status=status.HTTP_403_FORBIDDEN)
            found_url.delete()
            return Response({'message':'Succesful deleted'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserUrlListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        try:
            user = request.user
            urls = URL.objects.filter(user=user)
            serializer = AllURLSerializer(urls, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class RedirectView(APIView):
    def get(self, request, slug):
        try:
            # Another way to access the slug
            self_slug = self.kwargs['slug']
            url = URL.objects.get(slug=slug)
            redirect_serializer = RedirectSerializer(url)
            return HttpResponseRedirect(redirect_serializer.data['original_url'])
        except:
            raise Http404('Sorry this link is broken')
