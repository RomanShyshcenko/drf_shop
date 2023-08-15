from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import UpdateAPIView

from product.models import SubCategory
from product.permission import IsStaffOrSuperuserPermission


def get_object_by_name(name: str, model, detail: str):
    try:
        if name:
            return model.objects.get(name=name)
        raise ValidationError(code=status.HTTP_400_BAD_REQUEST)
    except model.DoesNotExist:
        raise NotFound(detail=detail)


class ActivateOrDeactivateCategoryAPIView(UpdateAPIView):
    authentication_classes = ()
    permission_classes = (IsStaffOrSuperuserPermission,)

    def get_object(self):
        name = self.request.data.get('name')
        detail = 'Category does not exist'
        return get_object_by_name(name=name, detail=detail, model=self.queryset)
