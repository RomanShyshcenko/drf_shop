from django.test import TestCase
from django.urls import resolve, reverse


class TestUrls(TestCase):

    def test_create_user_url(self):
        url = reverse('create_user')
        print(resolve(url))
