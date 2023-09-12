from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    DestroyAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from customer import serializers
from customer.services.client_service import UpdateUserAPIView, get_user
from customer.services import email_service

User = get_user_model()


class RegisterClientView(CreateAPIView):
    """Create User with email and password field"""
    serializer_class = serializers.RegisterUserSerializer
    authentication_classes = ()


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


class ChangeEmail(UpdateUserAPIView):
    """Change User email with setting is_confirmed_email to False"""
    serializer_class = serializers.ChangeUserEmaiSerializer


class DestroyUserView(DestroyAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        user_id = self.request.user.id
        return User.objects.get(id=user_id)


class SendEmailVerification(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user = self.request.user
        return email_service.send_verification_email(user)


class EmailVerification(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        user_id = self.request.query_params.get('user_id', '')
        confirmation_token = self.request.query_params.get('confirmation_token', '')
        try:
            user = User.objects.get(id=user_id)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user.is_confirmed_email:
            return Response('Email has already been verified.', status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, confirmation_token):
            user.is_confirmed_email = True
            user.save()
            return Response('Email successfully confirmed')

        return Response('Token is invalid or expired. Please request another confirmation email by signing in.',
                        status=status.HTTP_400_BAD_REQUEST)
