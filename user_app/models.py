from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core import validators
from django.db import models

from user_app.managers import CustomUserManager


# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        ("email address"),
        unique=True,
        validators=[validators.EmailValidator(message="Invalid Email")],
    )
    username = models.CharField(max_length=24)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"

    objects = CustomUserManager()

    def __str__(self):
        return self.username


class ResetToken(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    reset_token = models.CharField(max_length=40)
    created_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    encoded_user_id = models.CharField(max_length=20)
    blacklisted_token = models.CharField(max_length=40, null=True)

    def __str__(self):
        return self.reset_token
