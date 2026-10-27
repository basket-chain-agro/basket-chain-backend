from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class AuthAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_success(self):
        payload = {
            "fullName": "Buyer One",
            "email": "buyer@example.com",
            "phoneNumber": "+1234567890",
            "organization": "BasketChain",
            "location": "Lagos, Nigeria",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }

        response = self.client.post(
            "/api/v1/auth/register/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(
            email="buyer@example.com").exists())
        self.assertTrue(response.data["success"])
        self.assertIn("tokens", response.data["data"])
        self.assertEqual(response.data["data"]
                         ["user"]["fullName"], "Buyer One")

    def test_register_password_mismatch(self):
        payload = {
            "fullName": "Buyer Two",
            "email": "buyer2@example.com",
            "phoneNumber": "+1234567891",
            "organization": "BasketChain",
            "location": "Accra, Ghana",
            "password": "StrongPass123!",
            "password_confirm": "DifferentPass123!",
        }

        response = self.client.post(
            "/api/v1/auth/register/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["success"], False)

    def test_login_success(self):
        User.objects.create_user(
            email="login@example.com",
            username="loginuser",
            password="StrongPass123!",
            full_name="Login User",
            phone_number="+1000000000",
            location="Nairobi, Kenya",
        )

        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": "login@example.com", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("tokens", response.data["data"])

    def test_current_user_requires_auth(self):
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_user_success(self):
        user = User.objects.create_user(
            email="me@example.com",
            username="meuser",
            password="StrongPass123!",
            full_name="Me User",
            phone_number="+2000000000",
            location="Abuja, Nigeria",
        )
        refresh = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["email"], "me@example.com")
        self.assertEqual(response.data["data"]["fullName"], "Me User")
