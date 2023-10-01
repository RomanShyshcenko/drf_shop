from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from order.models import Order
from customer.permissions import IsStaffOrSuperuserPermission, HasCompleteAddressPermission, IsEmailVerifiedPermission
from order import serializers

User = get_user_model()


class CreateOrderAPIView(CreateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, HasCompleteAddressPermission, IsEmailVerifiedPermission)
    serializer_class = serializers.CreateOrderSerializer


class UpdateOrderStatusAPIView(APIView):
    authentication_classes = ()
    permission_classes = (IsStaffOrSuperuserPermission,)
    serializer_class = serializers.OrderStatusSerializer

    def patch(self, request):
        order_id = request.data.get('order_id')

        order = get_object_or_404(Order, id=order_id)

        serializer = self.serializer_class(order, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetOrdersListAPIView(ListAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.OrderListSerializer
    queryset = Order.objects.all()

    def get_object(self):
        user_id = self.request.user.id
        try:
            self.get_queryset().filter(buyer=user_id)
        except self.get_queryset().DoesNotExist:
            return Response(data="Your orders will be here.", status=status.HTTP_404_NOT_FOUND)


class GetOrderAPIView(RetrieveAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer

    def get_object(self):
        pk = self.request.query_params.get('id')
        return get_object_or_404(self.get_queryset().select_related('order_address'),
                                 buyer=self.request.user, id=pk)
