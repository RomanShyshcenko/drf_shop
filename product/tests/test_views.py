from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from product.models import Category, SubCategory, Product

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
        cls.activate_category_without_sub_category_url = reverse('enable_category')
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
            self.full_disable_category_url,
            {'name': 'Test Category', 'is_active': False}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Category.objects.get(name='Test Category').is_active)
        self.assertFalse(SubCategory.objects.get(name='Test SubCategory').is_active)

    def test_full_disable_category_with_invalid_data(self):
        response = self.client.put(
            self.full_disable_category_url,
            {'is_active': 'invalid_value'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Category.objects.get(name="Test Category").is_active)

    def test_activate_category_with_valid_data(self):
        cat = Category.objects.get(name='Test Category')
        cat.is_active = False
        cat.save()
        response = self.client.put(
            self.activate_category_without_sub_category_url,
            {'name': 'Test Category', 'is_active': True}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Category.objects.get(name="Test Category").is_active)

    def test_activate_category_with_invalid_data(self):
        cat = Category.objects.get(name='Test Category')
        cat.is_active = False
        cat.save()

        response_400 = self.client.put(
            self.activate_category_without_sub_category_url,
            {'name': 'Test Category', 'is_active': '8'}
        )
        response_404 = self.client.put(
            self.activate_category_without_sub_category_url,
            {'name': '123', 'is_activa': True}
        )

        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Category.objects.get(name="Test Category").is_active)
        self.assertEqual(response_404.status_code, status.HTTP_404_NOT_FOUND)


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
        cls.sub_category_activate_url = reverse('enable_sub_category')
        cls.activate_sub_categories_of_concrete_category_url = reverse(
            'activate_sub_categories_of_concrete_category')

    def setUp(self) -> None:
        self.client.force_authenticate(user=self.user)

    def test_create_sub_category(self):
        response = self.client.post(
            path=self.sub_category_create_url,
            data={'name': 'Test', 'category_id': 4})

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

    def test_activate_sub_category_with_valid_data(self):
        self.sub_category.is_active = False
        self.sub_category.save()
        response = self.client.put(
            path=self.sub_category_activate_url,
            data={'name': 'test', 'is_active': True}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(SubCategory.objects.get(name='test').is_active)

    def test_activate_sub_category_with_invalid_data(self):
        response_400 = self.client.put(
            path=self.sub_category_activate_url,
            data={'name': 'test', 'is_active': '21'}
        )
        response_404 = self.client.put(
            path=self.sub_category_activate_url,
            data={'name': 'testd', 'is_active': True}
        )

        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_404.status_code, status.HTTP_404_NOT_FOUND)

    def test_activate_sub_categories_of_concrete_category_with_valid_data(self):
        SubCategory.objects.create(name='test1', category_id=self.category, is_active=False)
        SubCategory.objects.create(name='test2', category_id=self.category, is_active=False)
        response = self.client.put(
            path=self.activate_sub_categories_of_concrete_category_url,
            data={'name': "Test Category", 'is_active': True}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        list_of_cat = SubCategory.objects.filter(category_id=self.category)
        for cat in list_of_cat:
            self.assertTrue(cat.is_active)

    def test_activate_sub_categories_of_concrete_category_with_invalid_data(self):
        response_400 = self.client.put(
            path=self.activate_sub_categories_of_concrete_category_url,
            data={'name': "Test Category", 'is_active': '123'}
        )
        response_404 = self.client.put(
            path=self.activate_sub_categories_of_concrete_category_url,
            data={'name': "False", 'is_active': True}
        )

        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_404.status_code, status.HTTP_404_NOT_FOUND)


class TestProductViews(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_staff(
            email='test@email.com', password='12345678'
        )
        cls.create_product_url = reverse('create_product')
        cls.is_active_status_url = reverse('is_active_status_product')
        cls.update_product_url = reverse('update_product')
        cls.get_product_url = reverse('product_detail')
        cls.category = Category.objects.create(name="Test Category_product")
        cls.sub_category = SubCategory.objects.create(
            name='test_product', category_id=Category.objects.get(name='Test Category_product')
        )
        cls.product = Product.objects.create(
            category_id=SubCategory.objects.get(name="test_product"),
            name='Test', brand='brand', description='description')

    def setUp(self) -> None:
        self.client.force_authenticate(user=self.user)

    def test_create_product_with_valid_data(self):
        response = self.client.post(
            path=self.create_product_url,
            data={
                "category_id": 2,
                "name": 'product',
                "brand": 'brand',
                "price": 1000,
                "description": 'description',
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_create_product_with_invalid_data(self):
        response_invalid_type = self.client.post(
            path=self.create_product_url,
            data={
                "category_id": False,
                "name": 'product',
                "brand": 'brand',
                "description": 'description',
            }
        )
        response_no_data = self.client.post(
            path=self.create_product_url,
            data={}
        )

        self.assertEqual(response_invalid_type.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_no_data.status_code, status.HTTP_400_BAD_REQUEST)

    def test_is_active_status_with_valid_data(self):
        response_deactivate = self.client.put(
            path=self.is_active_status_url,
            data={
                'id': 1,
                'is_active': False
            }
        )

        self.assertFalse(Product.objects.get(id=1).is_active)
        self.assertEqual(response_deactivate.status_code, status.HTTP_200_OK)

        self.product.is_active = False
        self.product.save()
        response_activate = self.client.put(
            path=self.is_active_status_url,
            data={
                'id': 1,
                'is_active': True
            }
        )

        self.assertEqual(response_activate.status_code, status.HTTP_200_OK)
        self.assertTrue(Product.objects.get(id=1).is_active)

    def test_update_product_with_valid_data(self):
        response = self.client.put(
            path=self.update_product_url,
            data={
                "id": 1,
                "name": "Iphone 10",
                "brand": "Samsung",
                "description": "New Iphone!",
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(id=1).brand, "Samsung")

    def test_update_product_with_invalid_data(self):
        response_400 = self.client.put(
            path=self.update_product_url,
            data={
                "id": False,
                "name": "Iphone 10",
                "brand": "Samsung",
                "description": "New Iphone!",
            }
        )
        response_404 = self.client.put(
            path=self.update_product_url,
            data={
                "id": 1234,
                "name": "Iphone 10",
                "brand": "Samsung",
                "description": "New Iphone!",
            }
        )
        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_404.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(Product.objects.get(id=1).brand, "Samsung")

    def test_get_product_with_valid_data(self):
        response = self.client.get(
            path=self.get_product_url + "?id=1"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_product_with_invalid_data(self):
        response_400 = self.client.get(
            path=self.get_product_url + "?id=fjfjfjf"
        )

        response_404 = self.client.get(
            path=self.get_product_url + "?id=21"
        )

        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_404.status_code, status.HTTP_404_NOT_FOUND)
