import json
import copy
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken

from customer.tests.test_views import create_staff_user_test_data
from product.models import Product
from product.tests.test_views import create_category_test_data, create_subcategory_test_data, create_product_test_data
from order.models import Order, OrderItem, DeliveryAddress

User = get_user_model()


def create_order_test_data(user: User) -> Order:
    return Order.objects.create(buyer=user)


def create_delivery_address_test_data(order: Order) -> DeliveryAddress:
    return DeliveryAddress.objects.create(
        order=order, city='test_city', street_address='test_street',
        apartment_address='test_apart', postal_code='test_code'
    )


def create_order_item_test_data(order: Order, product: Product) -> OrderItem:
    return OrderItem.objects.create(
        order=order, product=product, quantity=10
    )


class TestOrderViews(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff_user = create_staff_user_test_data()
        user = cls.user = User.objects.create(email='not_staff@test.com', password='12345678')
        user.is_confirmed_email = True
        user.save()

        cls.order_create_url = reverse('order_create')
        cls.order_details_url = reverse('order_details')
        cls.order_status_update_url = reverse('order_status_update')
        cls.order_all_url = reverse('order_all')

        cls.order = create_order_test_data(cls.user)
        cls.delivery_address = create_delivery_address_test_data(cls.order)
        cls.category = create_category_test_data()
        cls.subcategory = create_subcategory_test_data(cls.category)
        cls.product = create_product_test_data(cls.subcategory)
        cls.order_item = create_order_item_test_data(order=cls.order, product=cls.product)

    def setUp(self) -> None:
        self.token = AccessToken.for_user(self.user)
        self.create_order_data = {
            'delivery_address': {
                'city': 'test_city', 'street_address': 'test_street',
                'apartment_address': 'test_apart', 'postal_code': 'test_code'
            },
            'use_new_address': True,
            'order_items': [
                {
                    'product': self.product.id, 'quantity': 9
                }
            ]
        }

    def test_create_order_valid_data(self):
        response_with_new_address = self.client.post(
            self.order_create_url, data=json.dumps(self.create_order_data),
            content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {str(self.token)}"
        )
        # create new data without delivery address
        data = copy.deepcopy(self.create_order_data)
        data['use_new_address'] = False
        data.pop('delivery_address')
        # CREATE ADDRESS FOR USER
        address = self.user.address
        address.city = 'test_city'
        address.street_address = 'test_street'
        address.apartment_address = 'test_apart'
        address.postal_code = 'test_code'
        address.save()

        response_without_new_address = self.client.post(
            self.order_create_url, data=json.dumps(data), content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {str(self.token)}"
        )

        order = Order.objects.get(id=2)
        self.assertEqual(response_without_new_address.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_with_new_address.status_code, status.HTTP_201_CREATED)
        self.assertTrue(DeliveryAddress.objects.filter(order=order).exists())
        self.assertTrue(OrderItem.objects.filter(order=order).exists())

    def test_create_order_invalid_data(self):
        not_complete_address = copy.deepcopy(self.create_order_data)
        not_complete_address['delivery_address']['postal_code'] = ''
        no_items = copy.deepcopy(self.create_order_data)
        no_items.pop('order_items')
        out_of_product = copy.deepcopy(self.create_order_data)
        out_of_product['order_items'][0]['quantity'] = 120

        response_no_items_400 = self.client.post(
            self.order_create_url, data=json.dumps(no_items),
            content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {str(self.token)}"
        )
        response403 = self.client.post(
            self.order_create_url, data=json.dumps(not_complete_address),
            content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {str(self.token)}"
        )
        response_out_of_product_400 = self.client.post(
            self.order_create_url, data=json.dumps(out_of_product),
            content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {str(self.token)}"
        )

        self.assertEqual(response403.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_no_items_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_out_of_product_400.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_detail_valid_data(self):
        response = self.client.get(
            path=self.order_details_url + '?id=1', HTTP_AUTHORIZATION=f"Bearer {str(self.token)}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_detail_invalid_data(self):
        response = self.client.get(
            path=self.order_details_url + '?id=200', HTTP_AUTHORIZATION=f"Bearer {str(self.token)}"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_order_valid_data(self):
        response = self.client.get(
            path=self.order_all_url, HTTP_AUTHORIZATION=f"Bearer {str(self.token)}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
