from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication


from customer import serializers
from customer.models import UserAddresses, PhoneNumbers

User = get_user_model()


class UpdateUserAPIView(UpdateAPIView):
    """Updates User fields by given serializer class"""
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User

    def get_object(self) -> User:
        user_id = self.request.user.id
        return self.queryset.objects.get(id=user_id)

    def update(self, request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Updated successes"})
        else:
            return Response({"message": "failed", "details": serializer.errors})


def get_user(user_id: str) -> dict:
    user = User.objects.get(id=user_id)
    address = UserAddresses.objects.get(user_id=user)
    phone_number = PhoneNumbers.objects.get(user_id=user)

    return {
        "id": user.id,
        "email": user.email,
        "is_confirmed_email": user.is_confirmed_email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "address": address,
        "phone_number": phone_number
    }


def get_client_by_email(email: str) -> dict:
    """filtering client by email"""
    if email:
        client = User.objects.get(
            is_staff=False, is_superuser=False,
            is_active=True, email=email
            )
        if client:
            serializer = serializers.UserSerializer(client)
            return {'customer': serializer.data, 'status': status.HTTP_200_OK}
        return {
            'message': f'Account with this email {email} doesnt exist',
            'status': status.HTTP_404_NOT_FOUND
        }
    return {
        'message': 'Pleas enter the email',
        'status': status.HTTP_400_BAD_REQUEST
    }

