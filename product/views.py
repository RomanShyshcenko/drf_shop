from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    CreateAPIView, RetrieveAPIView,
    ListAPIView, UpdateAPIView
)
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from product.models import Category, SubCategory, Product
from customer.permissions import IsStaffOrSuperuserPermission
from product import serializers
from product.services.category_services import ActivateOrDeactivateCategoryAPIView
from product.services.product_services import get_product_by_id


class CreateProductView(CreateAPIView):
    """
    Create a new product with basic information.
    Additional fields are set automatically.
    """
    authentication_classes = ()
    permission_classes = (IsStaffOrSuperuserPermission,)
    serializer_class = serializers.CreateProductSerializer


class UpdateProductView(UpdateAPIView):
    """
    Update selected fields of a product.
    Can update name, brand, description, price and quantity.
    """
    authentication_classes = ()
    permission_classes = (IsStaffOrSuperuserPermission,)
    serializer_class = serializers.UpdateProductSerializer
    queryset = Product

    def get_object(self):
        product_id = self.request.data.get('id')
        return get_product_by_id(product_id)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_data = serializer.to_representation(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)


class IsActivaStatusProductView(UpdateAPIView):
    """
    Update the is_active status of a product.
    Can set is_active to True or False.
    """
    authentication_classes = ()
    permission_classes = (IsStaffOrSuperuserPermission,)
    serializer_class = serializers.IsActiveStatusProductSerializer
    queryset = Product

    def get_object(self):
        product_id = self.request.data.get('id')
        return get_product_by_id(product_id)


class GetProduct(RetrieveAPIView):
    """
    Retrieve product details by ID.
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.GetProductSerializer

    def get_object(self):
        product_id = self.request.query_params.get('id')
        return get_product_by_id(product_id)


class CreateCategory(CreateAPIView):
    """
    Create a new category.
    """
    authentication_classes = ()
    permission_classes = (IsStaffOrSuperuserPermission,)
    serializer_class = serializers.CategorySerializer


class GetCategoryListView(ListAPIView):
    """
    This class retrieve list of categories.
    """
    authentication_classes = ()
    serializer_class = serializers.CategorySerializer
    queryset = Category.objects.all()


class CategoryDisableSubcategoriesView(UpdateAPIView):
    """
    Disable a category along with its subcategories.
    """
    authentication_classes = ()
    permission_classes = (IsStaffOrSuperuserPermission,)
    serializer_class = serializers.CategorySerializer
    queryset = Category

    def disable_category_and_subcategories(self, category) -> None:
        category.is_active = False
        category.save()

        subcategories = SubCategory.objects.filter(category=category.pk, is_active=True)
        for subcategory in subcategories:
            self.disable_category_and_subcategories(subcategory)

    def get_object(self):
        name = self.request.data.get('name')
        return get_object_or_404(self.queryset, name=name)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if not instance.is_active:
            raise ValidationError({'message': 'Category already disabled!'})

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if not instance.is_active:
            self.disable_category_and_subcategories(instance)

        return Response(serializer.data)


class ActivateSubCategoriesAPIView(ActivateOrDeactivateCategoryAPIView):
    """
    Activate subcategories of a specific category.
    """
    serializer_class = serializers.ActivateSubCategoriesSerializer
    queryset = Category

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        response_data = serializer.update(instance, serializer.validated_data)

        return Response(response_data, status=status.HTTP_200_OK)


class UpdateStatusCategoryView(ActivateOrDeactivateCategoryAPIView):
    """Update status of concrete category,
    if category disabling along with related products.
    """
    serializer_class = serializers.UpdateStatusCategorySerializer
    queryset = Category


class UpdateStatusSubCategoryView(ActivateOrDeactivateCategoryAPIView):
    """
    Update status of concrete sub category,
    if sub category disabling along with related products.
    """
    serializer_class = serializers.UpdateStatusSubCategorySerializer
    queryset = SubCategory


class CreateSubCategory(CreateAPIView):
    authentication_classes = ()
    permission_classes = (IsStaffOrSuperuserPermission,)
    serializer_class = serializers.CreateSubCategorySerializer


class ProductsListAPIView(ListAPIView):
    """
    This class defines a view for listing products
    with optional filtering and ordering.
    """
    authentication_classes = []
    serializer_class = serializers.GetProductSerializer
    pagination_class = PageNumberPagination
    filter_backends = [OrderingFilter, DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'description', 'brand']
    filter_fields = ['name', 'brand', 'category_id__name']
    ordering_fields = ['price']

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset
