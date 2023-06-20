import json
import jwt

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from rest_framework_simplejwt.tokens import AccessToken

from customer.models import User, UserAddress, PhoneNumber


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

        no_data_response = self.client.post(url, {})
        no_passwords_response = self.client.post(url, {
            "email": "example@gmail.com",
            "password": "",
            "confirm_password": ""
        })
        invalid_email_response = self.client.post(url, {
            "email": "example_gmail.com",
            "password": "12345678",
            "confirm_password": "12345678"
        })
        email_already_exist_response = self.client.post(url, {
            "email": "test@email.com",
            "password": "12345678",
            "confirm_password": "12345678"
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
        self.assertEquals(no_passwords_response.status_code, 400)
        self.assertEquals(invalid_email_response.status_code, 400)
        self.assertEquals(email_already_exist_response.status_code, 400)
        self.assertEquals(no_confirm_password_response.status_code, 400)
        self.assertEquals(invalid_confirm_password_response.status_code, 400)

    def test_get_user_view(self):
        # test get user with valid jwt access token
        response = self.client.get(
            HTTP_AUTHORIZATION=f"Bearer {str(self.token)}",
            path=self.get_user_url
        )
        self.assertEquals(response.status_code, 200)

    def test_error_get_user(self):
        # test get user with invalid or expired jwt access token
        response = self.client.get(
            HTTP_AUTHORIZATION=f"Bearer {str(self.token) + 'boom'}",
            path=self.get_user_url
        )
        self.assertEquals(response.status_code, 401)

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
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {str(self.token)}"
        )

        try:
            User.objects.get(email="example@gmail.com", is_confirmed_email=False)
            is_user_exist = True
        except User.DoesNotExist:
            is_user_exist = False

        self.assertEquals(response.status_code, 200)
        self.assertEquals(is_user_exist, True)


