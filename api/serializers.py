from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from api.shortener import generate_slug
from linkshorter_backend import settings
from .models import URL
from rest_framework_simplejwt.tokens import RefreshToken

UserModel = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('email', 'password')
    def create(self, clean_data):
        user_obj = UserModel.objects.create_user(
            email=clean_data['email'],
            password=clean_data['password']
        )
        user_obj.save()
        return user_obj

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=255)
    ##
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        # Authenticate user
        user = authenticate(email=email, password=password)
        ##
        if not user:
            raise AuthenticationFailed('Invalid email or password.')
        ##
        refresh = RefreshToken.for_user(user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        ##
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('email', 'username')

class AllURLSerializer(serializers.ModelSerializer):
    original_url = serializers.URLField(max_length=500)
    slug = serializers.CharField(max_length=10)
    class Meta:
        model = URL
        fields = ('id', 'original_url', 'slug')

class URLSerializer(serializers.ModelSerializer):
    original_url = serializers.URLField(max_length=500)
    slug = serializers.CharField(max_length=20, required=False)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = URL
        fields = ('id', 'original_url', 'slug', 'user')
    ##
    def create(self, validated_data):
        slug = validated_data.pop('slug', None)
        if not slug:
            slug = generate_slug()
        return URL.objects.create(slug=slug, **validated_data)
    ##
    def update(self, instance, validated_data):
        instance.slug = validated_data.get('slug', instance.slug)
        instance.original_url = validated_data.get('original_url', instance.original_url)
        return super().update(instance, validated_data)


class NotAuthenticatedURLSerializer(serializers.ModelSerializer):
    original_url = serializers.URLField(max_length=500)
    slug = serializers.CharField(max_length=20, required=False)
    user = serializers.HiddenField(default=None)
    class Meta:
        model = URL
        fields = ('original_url','slug', 'user')
    ##
    def create(self, validated_data):
        user = validated_data.pop('user', None)
        if not user:
            default_user = UserModel.objects.get(email=settings.DEFAULT_USER_EMAIL)
            validated_data['user'] = default_user
        ##
        slug = validated_data.pop('slug', None)
        if slug:
            raise PermissionDenied('Slug shouldn\'t be send as anonymous user.')
        else:
            slug = generate_slug()
        return URL.objects.create(slug=slug, **validated_data)


class RedirectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = URL
        fields = ('original_url','slug')
        lookup_field = 'slug'