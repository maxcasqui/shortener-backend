from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import ValidationError
from api.models import URL
from .validations import validate_data, validate_url
from .serializers import AllURLSerializer, NotAuthenticatedURLSerializer, UserRegisterSerializer, UserLoginSerializer, UserSerializer, URLSerializer

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
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        clean_data = validate_url(request.data)
        ##
        if clean_data is None:
            return Response({'error': 'Invalid URL'}, status=status.HTTP_400_BAD_REQUEST)
        ##
        serializer = URLSerializer(data=clean_data, context={'request': request})
        if serializer.is_valid():
            instance = serializer.save()
            return Response({'slug': instance.slug}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotAuthenticatedUserUrlView(APIView):
    permission_classes = (permissions.AllowAny,)
    ##
    def post(self, request):
        clean_data = validate_url(request.data)
        ##
        serializer = NotAuthenticatedURLSerializer(data=clean_data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response({'slug': instance.slug}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUrlListView(APIView):
    def get(self, request):
        user = request.user
        urls = URL.objects.filter(user=user)
        serializer = AllURLSerializer(urls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)