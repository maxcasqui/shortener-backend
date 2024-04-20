from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class AppUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required.')
        if not password:
            raise ValueError('Password is required.')
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_staff', True)
        if not email:
            raise ValueError('Email is required.')
        if not password:
            raise ValueError('Password is required.')
        user = self.create_user(email, password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.is_verified = True
        user.save()
        return user

class AppUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=80)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = AppUserManager()
    ##
    def __str__(self):
        return self.username

class URL(models.Model):
    original_url = models.URLField(max_length=500)
    slug = models.CharField(max_length=10)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.original_url} - {self.slug}'