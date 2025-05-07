from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password) 
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20)
    code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email
