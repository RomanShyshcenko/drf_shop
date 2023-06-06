import uuid
import bcrypt

from django.core.validators import RegexValidator, MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from backend.customer.services.managers import CustomUserManager

phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the "
            "format: '+999999999'. Up to 15 digits allowed."
)


class User(AbstractBaseUser, PermissionsMixin):
    username = None
    id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4
    )
    email = models.EmailField(
        unique=True
    )
    first_name = models.CharField(
        max_length=30, blank=True
    )
    last_name = models.CharField(
        max_length=30, blank=True
    )
    password = models.CharField(
        max_length=256,
        validators=[MinValueValidator(8)],
        blank=True
    )

    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_confirmed_email = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def verify_password(self, raw_password):
        return bcrypt.checkpw(raw_password, self.password.encode('utf8'))

    class Meta:
        db_table = 'user'
        ordering = ('-date_joined',)


class PhoneNumber(models.Model):
    user = models.ForeignKey(
        User, related_name='phone',
        on_delete=models.CASCADE
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        unique=True,
        null=True
    )
    is_verified = models.BooleanField(default=False)
    sent = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user_id

    class Meta:
        ordering = ('-created_at', )
        db_table = 'phone_number'


class UserAddress(models.Model):
    user = models.ForeignKey(User, related_name='address', on_delete=models.CASCADE)

    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user_id

    class Meta:
        ordering = ('-created_at', )
        db_table = 'address'




