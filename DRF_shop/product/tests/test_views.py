from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

from customer.tests.test_views import create_staff_user_test_data
from product.models import Category, SubCategory, Product

User = get_user_model()


def create_category_test_data() -> Category:
    return Category.objects.create(name="Test Category")


def create_subcategory_test_data(category: Category) -> SubCategory:
    return SubCategory.objects.create(category=category, name='Test SubCategory')


def create_product_test_data(subcategory: SubCategory) -> Product:
    return Product.objects.create(
        name='Iphone 10', description='test',
        price=1000, quantity=100, brand='Apple',
        category=subcategory
    )


class TestCategoryViews(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a staff user for authentication
        cls.user = User.objects.create_staff(
            email='staff@test.com', password='12345678'
        )
        # Define URLs
        cls.create_category_url = reverse('create_category')
        cls.update_category_status_url = reverse('update_category_status')
        # Create initial data
        cls.category = create_category_test_data()
        cls.subcategory = create_subcategory_test_data(cls.category)

    def setUp(self) -> None:
        # Authenticate the client with the staff user
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

    def test_deactivate_category_with_valid_data(self):
        cat_name = self.category.name
        response = self.client.put(
            self.update_category_status_url,
            {'name': cat_name, 'is_active': False}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Category.objects.get(name=cat_name).is_active)
        self.assertFalse(SubCategory.objects.get(name=self.subcategory.name).is_active)

    def test_update_status_category_with_invalid_data(self):
        response = self.client.put(
            self.update_category_status_url,
            {'name': 'Test Category', 'is_active': 'invalid_value'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Category.objects.get(name=self.category.name).is_active)

    def test_activate_category_with_valid_data(self):
        cat_name = self.category.name
        self.category.is_active = False
        self.category.save()
        response = self.client.put(
            self.update_category_status_url,
            {'name': cat_name, 'is_active': True}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Category.objects.get(name=cat_name).is_active)

    def test_activate_category_with_invalid_data(self):
        self.category.is_active = False
        self.category.save()

        # Test different invalid scenarios
        response_invalid_value = self.client.put(
            self.update_category_status_url,
            {'name': 'Test Category', 'is_active': '8'}
        )
        response_invalid_key = self.client.put(
            self.update_category_status_url,
            {'name': '123', 'is_activa': True}
        )

        self.assertEqual(response_invalid_value.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Category.objects.get(name="Test Category").is_active)
        self.assertEqual(response_invalid_key.status_code, status.HTTP_404_NOT_FOUND)


class TestSubCategoryView(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_staff_user_test_data()
        cls.category = create_category_test_data()
        cls.sub_category = create_subcategory_test_data(cls.category)

        cls.create_sub_category_url = reverse('create_sub_category')
        cls.update_sub_category_status_url = reverse('update_sub_category_status')
        cls.activate_subcategories_url = reverse('activate_subcategories')

    def setUp(self) -> None:
        self.client.force_authenticate(user=self.user)

    def test_create_sub_category(self):
        response = self.client.post(
            path=self.create_sub_category_url,
            data={'name': 'Test', 'category': self.category.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_disable_sub_category(self):
        response = self.client.put(
            path=self.update_sub_category_status_url,
            data={'name': self.sub_category.name, 'is_active': False}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_status_sub_category_with_invalid_data(self):
        self.sub_category.is_active = False
        self.sub_category.save()

        response_invalid_type = self.client.put(
            path=self.update_sub_category_status_url,
            data={'name': self.sub_category.name, 'is_active': '2'}
        )
        response_invalid_name = self.client.put(
            path=self.update_sub_category_status_url,
            data={'name': 1, 'is_active': False}
        )
        response_sub_category_already_disabled = self.client.put(
            path=self.update_sub_category_status_url,
            data={'name': self.sub_category.name, 'is_active': False}
        )

        self.assertEqual(response_invalid_type.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_invalid_name.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_sub_category_already_disabled.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_sub_category_with_valid_data(self):
        self.sub_category.is_active = False
        self.sub_category.save()
        response = self.client.put(
            path=self.update_sub_category_status_url,
            data={'name': self.sub_category.name, 'is_active': True}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(SubCategory.objects.get(name=self.sub_category.name).is_active)

    def test_activate_subcategories_with_valid_data(self):
        SubCategory.objects.create(name='test1', category=self.category, is_active=False)
        response = self.client.put(
            path=self.activate_subcategories_url,
            data={'name': "Test Category", 'is_active': True}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        subcategories = SubCategory.objects.filter(category=self.category)
        for subcategory in subcategories:
            self.assertTrue(subcategory.is_active)

    def test_activate_subcategories_with_invalid_data(self):
        response_400 = self.client.put(
            path=self.activate_subcategories_url,
            data={'name': "Test Category", 'is_active': '123'}
        )
        response_404 = self.client.put(
            path=self.activate_subcategories_url,
            data={'name': "False", 'is_active': True}
        )

        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_404.status_code, status.HTTP_404_NOT_FOUND)


class TestProductViews(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_staff_user_test_data()
        cls.create_product_url = reverse('create_product')
        cls.is_active_status_url = reverse('is_active_status_product')
        cls.update_product_url = reverse('update_product')
        cls.get_product_url = reverse('product_detail')
        cls.category = create_category_test_data()
        cls.sub_category = create_subcategory_test_data(cls.category)
        cls.product = create_product_test_data(cls.sub_category)

    def setUp(self) -> None:
        self.client.force_authenticate(user=self.user)

    def test_create_product_with_valid_data(self):
        response = self.client.post(
            path=self.create_product_url,
            data={
                "category": self.sub_category.id,
                "name": 'product',
                "brand": 'brand',
                "price": 1000,
                "quantity": 20,
                "description": 'description',
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_create_product_with_invalid_data(self):
        response_invalid_type = self.client.post(
            path=self.create_product_url,
            data={
                "category": False,
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
        product_id = self.product.id
        response_deactivate = self.client.put(
            path=self.is_active_status_url,
            data={
                'id': product_id,
                'is_active': False
            }
        )

        self.assertFalse(Product.objects.get(id=product_id).is_active)
        self.assertEqual(response_deactivate.status_code, status.HTTP_200_OK)

        self.product.is_active = False
        self.product.save()
        response_activate = self.client.put(
            path=self.is_active_status_url,
            data={
                'id': product_id,
                'is_active': True
            }
        )

        self.assertEqual(response_activate.status_code, status.HTTP_200_OK)
        self.assertTrue(Product.objects.get(id=product_id).is_active)

    def test_update_product_with_valid_data(self):
        product_id = self.product.id
        response = self.client.put(
            path=self.update_product_url,
            data={
                "id": product_id,
                "name": "Iphone 10",
                "brand": "Samsung",
                "description": "New Iphone!",
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.get(id=product_id).brand, "Samsung")

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
        self.assertNotEqual(Product.objects.get(id=self.product.id).brand, "Samsung")

    def test_get_product_with_valid_data(self):
        response = self.client.get(
            path=self.get_product_url + f"?id={self.product.id}"
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
