from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        BUYER = "buyer", "Buyer"
        ORGANIZATION_ADMIN = "organization_admin", "Organization Admin"
        SUPERADMIN = "superadmin", "Super Admin"

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=False)
    full_name = models.CharField(max_length=255, blank=True, default="")
    phone_number = models.CharField(max_length=30, blank=True, default="")
    location = models.CharField(max_length=255, blank=True, default="")
    role = models.CharField(
        max_length=30, choices=Role.choices, default=Role.BUYER)
    organization = models.ForeignKey(
        "organizations.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="members",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email
