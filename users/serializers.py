from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify
from rest_framework import serializers

from organizations.models import Organization
from .models import User


class UserSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source="full_name", read_only=True)
    phoneNumber = serializers.CharField(source="phone_number", read_only=True)
    organization = serializers.SerializerMethodField()
    location = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "fullName",
            "email",
            "phoneNumber",
            "organization",
            "location",
            "role",
        ]
        read_only_fields = ["id"]

    def get_organization(self, obj):
        if not obj.organization:
            return None
        return obj.organization.name


class RegisterSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(
        source="full_name", write_only=True, required=True)
    phoneNumber = serializers.CharField(
        source="phone_number", write_only=True, required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    organization = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    location = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = User
        fields = [
            "fullName",
            "email",
            "phoneNumber",
            "organization",
            "location",
            "password",
            "password_confirm",
        ]

    def validate_email(self, value):
        email = value.lower().strip()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return email

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")

        org_name = validated_data.pop("organization", None)
        org = None
        if org_name:
            org, _ = Organization.objects.get_or_create(
                name=org_name,
                defaults={"slug": slugify(org_name) or "organization"},
            )

        email = validated_data["email"].lower().strip()
        base_username = email.split("@")[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            full_name=validated_data.get("full_name", "").strip(),
            phone_number=validated_data.get("phone_number", "").strip(),
            location=validated_data.get("location", "").strip(),
            organization=org,
            role=User.Role.BUYER,
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email").lower().strip()
        password = attrs.get("password")

        user = authenticate(request=None, username=email, password=password)
        if not user or not user.is_active:
            raise serializers.ValidationError("Invalid email or password.")

        attrs["user"] = user
        return attrs
