from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from product.models import Category, SubCategory

User = get_user_model()


class TestCategoryViews(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # user for auth
        cls.user = User.objects.create_staff(
            email='test@email.com', password='12345678'
        )
        # urls
        cls.create_category_url = reverse('create_category')
        cls.full_disable_category_url = reverse('disable_category_and_subcategories')
        # models
        Category.objects.create(name="Test Category")
        SubCategory.objects.create(category_id=Category.objects.get(name='Test Category'), name='Test SubCategory')

    def setUp(self) -> None:
        self.client.force_authenticate(user=self.user)

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

    def test_full_disable_category_with_valid_data(self):
        response = self.client.put(
            self.full_disable_category_url, {'name': 'Test Category', 'is_active': False}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Category.objects.get(name='Test Category').is_active)
        self.assertFalse(SubCategory.objects.get(name='Test SubCategory').is_active)

    def test_full_disable_category_with_invalid_data(self):
        response = self.client.put(
            self.full_disable_category_url, {'is_active': 'invalid_value'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Category.objects.get(name="Test Category").is_active)


class TestSubCategoryView(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_staff(
            email='test@email.com', password='12345678'
        )
        cls.category = Category.objects.create(name="Test Category")
        cls.sub_category = SubCategory.objects.create(
            name='test', category_id=Category.objects.get(name='Test Category')
        )
        cls.sub_category_create_url = reverse('create_sub_category')
        cls.sub_category_disable_url = reverse('disable_sub_category')

    def setUp(self) -> None:
        self.client.force_authenticate(user=self.user)

    def test_create_sub_category(self):
        response = self.client.post(
            path=self.sub_category_create_url,
            data={'name': 'Test', 'category_id': 3})

        self.assertEqual(response.status_code, 201)

    def test_disable_sub_category(self):
        response = self.client.put(
            path=self.sub_category_disable_url,
            data={'name': 'test', 'is_active': False}
        )

        self.assertEqual(response.status_code, 200)

    def test_disable_sub_category_with_invalid_data(self):
        self.sub_category.is_active = False
        self.sub_category.save()
        response_invalid_type = self.client.put(
            path=self.sub_category_disable_url,
            data={'name': 'test', 'is_active': '2'}
        )
        response_invalid_name = self.client.put(
            path=self.sub_category_disable_url,
            data={'name': 1, 'is_active': False}
        )
        response_sub_category_already_disabled = self.client.put(
            path=self.sub_category_disable_url,
            data={'name': 'test', 'is_active': False}
        )

        self.assertEqual(response_invalid_type.status_code, 400)
        self.assertEqual(response_invalid_name.status_code, 404)
        self.assertEqual(response_sub_category_already_disabled.status_code, 400)
