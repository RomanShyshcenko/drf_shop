from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    DestroyAPIView,
)
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication


from customer.services.client_service import UpdateUserAPIView, get_user
from customer import serializers
from customer.models import User, UserAddress, PhoneNumber


class RegisterClientView(CreateAPIView):
    """Create User with email and password field"""
    serializer_class = serializers.RegisterUserSerializer
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED, headers=self.headers)


class RetrieveUserView(RetrieveAPIView):
    """Retrieve User by JWT Authentication"""
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.UserSerializer

    def get_object(self):
        """Get user"""
        user_id = self.request.user.id
        return get_user(user_id=user_id)


class UpdateUserView(UpdateUserAPIView):
    """Create or update user first_name, last_name and address fields"""
    serializer_class = serializers.UserSerializer


class ChangePasswordView(UpdateUserAPIView):
    """Change User password"""
    serializer_class = serializers.ChangePasswordSerializer


class DestroyUserView(DestroyAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        user_id = self.request.user.id
        return User.objects.filter(id=user_id)

