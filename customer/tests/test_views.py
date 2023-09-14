import json

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class TestUserViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.user = User.objects.create_user(email='test@email.com', password='12345678')

    def setUp(self):
        self.create_user_url = reverse('create_user')
        self.get_user_url = reverse('get_user')
        self.token_url = reverse('token_obtain_pair')
        self.update_user_url = reverse('update_user')
        self.change_email_url = reverse('change_email')
        self.token = AccessToken.for_user(self.user)

    def test_register_user_view(self):
        data = {
            "email": "example@gmail.com",
            "password": "12345678",
            "confirm_password": "12345678"
        }
        response = self.client.post(self.create_user_url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email=data['email']).exists())

    def test_error_register_user_view(self):
        url = self.create_user_url
        invalid_data = [
            {},  # No data
            {"email": "example@gmail.com", "password": "", "confirm_password": ""},  # No passwords
            {"email": "example_gmail.com", "password": "12345678", "confirm_password": "12345678"},  # Invalid email
            {"email": "test@email.com", "password": "12345678", "confirm_password": "12345678"},  # Email already exists
            {"email": "example@gmail.com", "password": "12345678", "confirm_password": ""},  # No confirm password
            {"email": "example@gmail.com", "password": "12345678", "confirm_password": "12345678999"},  # Invalid confirm password
        ]
        for data in invalid_data:
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, 400)

    def test_get_user_view(self):
        response = self.client.get(self.get_user_url, HTTP_AUTHORIZATION=f"Bearer {str(self.token)}")
        self.assertEqual(response.status_code, 200)

    def test_error_get_user(self):
        response = self.client.get(self.get_user_url, HTTP_AUTHORIZATION=f"Bearer {str(self.token) + 'boom'}")
        self.assertEqual(response.status_code, 401)

    def test_update_user(self):
        data = {
            "first_name": "Roman",
            "last_name": "Shyshchenko",
            "address": {
                "city": "kyiv",
                "street_address": "example",
                "apartment_address": "example",
                "postal_code": "04032"
            }
        }
        response = self.client.put(
            self.update_user_url,
            data=json.dumps(data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {str(self.token)}"
        )
        self.assertEqual(response.status_code, 200)

    def test_email_update(self):
        data = {
            "email": "example@gmail.com"
        }
        response = self.client.put(
            self.change_email_url,
            data=json.dumps(data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {str(self.token)}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(email=data['email'], is_confirmed_email=False).exists())
