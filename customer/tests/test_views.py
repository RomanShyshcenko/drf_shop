import json
import jwt

from django.test import TestCase, Client
from django.urls import reverse

from rest_framework_simplejwt.tokens import AccessToken

from customer.models import User, UserAddress, PhoneNumber
from core import settings


ACCESS_TOKEN_LIFETIME = settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME")
REFRESH_TOKEN_LIFETIME = settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME")
ALGORITHM = settings.SIMPLE_JWT.get("ALGORITHM")
SIGNING_KEY = settings.SIMPLE_JWT.get("SIGNING_KEY")


class TestUserViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create_user(email='test@email.com', password='12345678')

    def setUp(self):
        self.create_user_url = reverse('create_user')
        self.get_user_url = reverse('get_user')
        self.token_url = reverse('token_obtain_pair')

    def test_register_user_view(self):
        response = self.client.post(self.create_user_url, {
            "email": "example@gmail.com",
            "password": "12345678",
            "confirm_password": "12345678"
        })

        try:
            is_user_created = User.objects.get(email="example@gmail.com")
        except Exception as e:
            is_user_created = False
            print(e)

        self.assertTrue(is_user_created)
        self.assertEquals(response.status_code, 201)

    def test_error_register_user_view(self):
        url = self.create_user_url

        no_data_response = self.client.post(url, {

        })
        invalid_email_response = self.client.post(url, {
            "email": "example_gmail.com",
            "password": "12345678",
            "confirm_password": "12345678"
        })
        no_password_response = self.client.post(url, {
            "email": "example@gmail.com",
            "password": "",
            "confirm_password": ""
        })
        no_confirm_password_response = self.client.post(url, {
            "email": "example@gmail.com",
            "password": "12345678",
            "confirm_password": ""
        })
        invalid_confirm_password_response = self.client.post(url, {
            "email": "example@gmail.com",
            "password": "12345678",
            "confirm_password": "12345678999"
        })

        self.assertEquals(no_data_response.status_code, 400)
        self.assertEquals(no_password_response.status_code, 400)
        self.assertEquals(no_confirm_password_response.status_code, 400)
        self.assertEquals(invalid_confirm_password_response.status_code, 400)
        self.assertEquals(invalid_email_response.status_code, 400)

    def test_get_user_view(self):
        # test get user with valid jwt access token
        token = AccessToken.for_user(self.user)

        response = self.client.get(self.get_user_url, headers={"Authorization": f"Bearer {str(token)}"})

        self.assertEquals(response.status_code, 200)

    def test_error_get_user(self):
        # test get user with invalid jwt access token
        token = AccessToken.for_user(self.user)

        response = self.client.get(self.get_user_url, headers={"Authorization": f"Bearer {str(token) + 'boom'}"})
        
        self.assertEquals(response.status_code, 401)







