from django.shortcuts import get_object_or_404
from rest_framework.generics import UpdateAPIView

from customer.permissions import IsStaffOrSuperuserPermission


class ActivateOrDeactivateCategoryAPIView(UpdateAPIView):
    authentication_classes = ()
    permission_classes = (IsStaffOrSuperuserPermission,)

    def get_object(self):
        name = self.request.data.get('name')
        return get_object_or_404(self.queryset, name=name)
