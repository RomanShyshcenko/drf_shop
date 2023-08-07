from rest_framework import status
from rest_framework.generics import (
    CreateAPIView, RetrieveAPIView,
    DestroyAPIView, ListAPIView,
    UpdateAPIView
)
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from product.models import Category, SubCategory
from product.permission import IsStaffOrSuperuserPermission
from product import serializers


class CreateCategory(CreateAPIView):
    authentication_classes = ()
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
        try:
            if name:
                return self.get_queryset().objects.get(name=self.request.data.get('name'))
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            raise NotFound(detail='Category does not exist')

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if not instance.is_active:
            self.disable_category_and_subcategories(instance)
        return Response(serializer.data)


class CreateSubCategory(CreateAPIView):
    authentication_classes = ()
    permission_classes = (IsStaffOrSuperuserPermission,)
    serializer_class = serializers.CreateSubCategorySerializer

    def post(self, request, *args, **kwargs):
        cat_id = request.data.get('category_id')
        try:
            Category.objects.get(id=cat_id)
        except Category.DoesNotExist:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'message': f'Parent category with id:({cat_id}) does not exist'})

        self.create(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED, headers=self.headers)


class DisableSubCategoryView(UpdateAPIView):
    authentication_classes = ()
    permission_classes = (IsStaffOrSuperuserPermission,)
    serializer_class = serializers.DisableSubCategorySerializer
    queryset = SubCategory

    def get_object(self):
        name = self.request.data.get('name')
        try:
            if name:
                return self.get_queryset().objects.get(name=self.request.data.get('name'))
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except SubCategory.DoesNotExist:
            raise NotFound(detail='Category does not exist')

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_active:
            return Response(data={'message': 'Category already disabled!'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

