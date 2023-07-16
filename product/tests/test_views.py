from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from product.models import Category

User = get_user_model()


class TestCategoryViews(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_staff(
            email='test@email.com', password='12345678'
        )
        Category.objects.create(name="Test Category")

    def setUp(self) -> None:
        self.client.force_authenticate(user=self.user)
        self.create_category_url = reverse('create_category')
        self.disable_category_url = reverse('disable_category')

    def test_create_category_with_valid_data(self):
        response = self.client.post(self.create_category_url, {'name': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Category.objects.get(name='Test').name, 'Test')

    def test_create_category_with_invalid_data(self):
        data = {'name': ''}
        response = self.client.post(self.create_category_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Category.objects.count(), 1)

    def test_disable_category_with_valid_data(self):
        response = self.client.patch(
            self.disable_category_url, {'name': 'Test Category', 'is_active': False}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(Category.objects.get(name='Test Category').is_active, False)

    def test_disable_category_with_invalid_data(self):
        response = self.client.patch(
            self.disable_category_url, {'is_active': 'invalid_value'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Category.objects.get(name="Test Category").is_active)
