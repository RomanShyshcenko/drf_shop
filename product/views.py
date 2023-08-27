from rest_framework import status
from rest_framework.generics import (
    CreateAPIView, RetrieveAPIView,
    ListAPIView, UpdateAPIView
)
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from product.models import Category, SubCategory, Product
from customer.permissions import IsStaffOrSuperuserPermission
from product import serializers
from product.services.category_services import get_object_by_name, ActivateOrDeactivateCategoryAPIView
from product.services.product_services import get_product_by_id


class CreateProductView(CreateAPIView):
    """
    Create a new product with basic information.
    Additional fields are set automatically.
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.CreateProductSerializer


class UpdateProductView(UpdateAPIView):
    """
    Update selected fields of a product.
    Can update name, brand, description, price and quantity.
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.UpdateProductSerializer
    queryset = Product

    def get_object(self):
        product_id = self.request.data.get('id')
        try:
            int(product_id)
        except (ValueError, TypeError):
            raise ValidationError({
                'error': {'id': f'You should give a number!'}
            })

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
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            raise ValidationError(
                {'id': 'ID should be a valid integer'}
            )

        return get_product_by_id(product_id)


class CreateCategory(CreateAPIView):
    """
    Create a new category.
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.CategorySerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response(
            response.data,
            status=status.HTTP_201_CREATED,
            headers=response.headers
        )


class CategoryDisableSubcategoriesView(UpdateAPIView):
    """
    Disable a category along with its subcategories.
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.CategorySerializer
    queryset = Category

    def disable_category_and_subcategories(self, category) -> None:
        category.is_active = False
        category.save()

        subcategories = SubCategory.objects.filter(category_id=category.pk, is_active=True)
        for subcategory in subcategories:
            self.disable_category_and_subcategories(subcategory)

    def get_object(self):
        name = self.request.data.get('name')
        detail = 'Category does not exist'
        return get_object_by_name(name=name, model=self.queryset, detail=detail)

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


class ActivateSubCategoriesOfConcreteCategoryView(ActivateOrDeactivateCategoryAPIView):
    """
    Activate subcategories of a specific category.
    """
    serializer_class = serializers.ActivateSubCategoriesOfConcreteCategorySerializer
    queryset = Category

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        response_data = serializer.update(instance, serializer.validated_data)

        return Response(response_data, status=status.HTTP_200_OK)


class ActivateCategoryView(ActivateOrDeactivateCategoryAPIView):
    serializer_class = serializers.CategoryActivateSerializer
    queryset = Category


class DisableSubCategoryView(ActivateOrDeactivateCategoryAPIView):
    serializer_class = serializers.SubCategoryDisableSerializer
    queryset = SubCategory


class ActivateSubCategoryView(ActivateOrDeactivateCategoryAPIView):
    serializer_class = serializers.SubCategoryActivateSerializer
    queryset = SubCategory


class CreateSubCategory(CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.CreateSubCategorySerializer

    def post(self, request, *args, **kwargs):
        cat_id = request.data.get('category_id')

        try:
            Category.objects.get(id=cat_id)
        except Category.DoesNotExist:
            raise ValidationError({
                'message': f'Parent category with id:({cat_id}) does not exist'
            })

        self.create(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED, headers=self.headers)

