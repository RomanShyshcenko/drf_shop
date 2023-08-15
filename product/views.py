from rest_framework import status
from rest_framework.generics import (
    CreateAPIView, RetrieveAPIView,
    DestroyAPIView, ListAPIView,
    UpdateAPIView
)
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

from product.models import Category, SubCategory
from product.permission import IsStaffOrSuperuserPermission
from product import serializers
from product.services.category_services import get_object_by_name, ActivateOrDeactivateCategoryAPIView


class CreateCategory(CreateAPIView):
    authentication_classes = ()
    permission_classes = (IsStaffOrSuperuserPermission,)
    serializer_class = serializers.CategorySerializer

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED, headers=self.headers)


class CategoryDisableSubcategoriesView(UpdateAPIView):
    authentication_classes = ()
    permission_classes = (IsStaffOrSuperuserPermission,)
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
            raise ValidationError(detail={'message': 'Category already disabled!'}, code=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if not instance.is_active:
            self.disable_category_and_subcategories(instance)
        return Response(serializer.data)


class ActivateSubCategoriesOfConcreteCategoryView(ActivateOrDeactivateCategoryAPIView):
    serializer_class = serializers.ActivateSubCategoriesOfConcreteCategorySerializer
    queryset = Category

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        response_data = serializer.update(instance, serializer.validated_data)

        return Response(response_data, status=status.HTTP_200_OK)


class ActivateCategoryWithoutSubCategoriesView(ActivateOrDeactivateCategoryAPIView):
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
    permission_classes = (IsStaffOrSuperuserPermission,)
    serializer_class = serializers.CreateSubCategorySerializer

    def post(self, request, *args, **kwargs):
        cat_id = request.data.get('category_id')
        try:
            Category.objects.get(id=cat_id)
        except Category.DoesNotExist:
            raise ValidationError(code=status.HTTP_400_BAD_REQUEST,
                                  detail={'message': f'Parent category with id:({cat_id}) does not exist'})

        self.create(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED, headers=self.headers)

