from rest_framework import status
from rest_framework.generics import (
    CreateAPIView, RetrieveAPIView,
    DestroyAPIView, ListAPIView,
    UpdateAPIView
)
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from product.models import Category
from product.permission import IsStaffOrSuperuserPermission
from product import serializers


class CreateCategory(CreateAPIView):
    authentication_classes = ()
    permission_classes = (IsStaffOrSuperuserPermission,)
    serializer_class = serializers.CategorySerializer

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED, headers=self.headers)


class DisableCategory(UpdateAPIView):
    authentication_classes = ()
    permission_classes = (IsStaffOrSuperuserPermission,)
    serializer_class = serializers.DisableCategorySerializer
    queryset = Category

    def get_object(self):
        data = self.request.data
        try:
            if self.request.data.get('name'):
                return Category.objects.get(name=data.get('name'))
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            raise NotFound(detail='Category does not exist')

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data={"is_active": request.data.get('is_active')})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Category disabled successes"},
                            status=status.HTTP_200_OK)
        else:
            return Response({"message": "failed", "details": serializer.errors})


