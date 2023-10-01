from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.contrib.auth import get_user_model

from order.models import Order, OrderItem, DeliveryAddress

User = get_user_model()


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer class for serializing order items
    """

    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product', 'quantity',
                  'created_at', 'updated_at')
        read_only_fields = ('order',)

    def validate(self, validated_data):
        order_quantity = validated_data['quantity']
        product_quantity = validated_data['product'].quantity

        order_id = self.context['view'].kwargs.get('order_id')
        product_id = validated_data['product']
        current_item = OrderItem.objects.filter(
            order__id=order_id, product=product_id)

        if order_quantity > product_quantity:
            error = {'quantity': 'Ordered quantity is more than the stock.'}
            raise serializers.ValidationError(error)

        if not self.instance and current_item.count() > 0:
            error = {'product': 'Product already exists in your order.'}
            raise serializers.ValidationError(error)

        return validated_data


class DeliveryAddressSerializer(ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = ('id', 'city', 'street_address', 'apartment_address', 'postal_code', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class CreateOrderSerializer(ModelSerializer):
    """
    Serializer class for creating:
    orders, order items and delivery addresses.
    """
    buyer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    order_items = OrderItemSerializer(many=True)
    delivery_address = DeliveryAddressSerializer(required=False)
    use_new_address = serializers.BooleanField(default=False)

    class Meta:
        model = Order
        fields = ('id', 'buyer', 'status', 'order_items', 'delivery_address',
                  'created_at', 'updated_at', 'use_new_address')
        read_only_fields = ('status',)

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        new_address_data = validated_data.pop('delivery_address', False)
        use_new_address = validated_data.pop('use_new_address', False)
        order = Order.objects.create(**validated_data)

        for item_data in order_items_data:
            product = item_data['product']
            OrderItem.objects.create(order=order, **item_data)

            product.quantity = product.quantity - item_data['quantity']
            product.save()

        if use_new_address and new_address_data:
            DeliveryAddress.objects.create(order=order, **new_address_data)

        else:
            # refactor
            user_address = self.context['request'].user.address

            DeliveryAddress.objects.create(
                order=order,
                city=user_address.city,
                street_address=user_address.street_address,
                apartment_address=user_address.apartment_address,
                postal_code=user_address.postal_code
            )

        return order


class OrderSerializer(ModelSerializer):
    order_items = OrderItemSerializer(many=True)
    order_address = DeliveryAddressSerializer()

    class Meta:
        model = Order
        fields = '__all__'


class OrderStatusSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',)

    def validate(self, attrs):
        order_status = self.instance.status
        if order_status == 'C':
            raise ValidationError("Order is cancelled, you can't change the status")
        elif order_status == 'D':
            raise ValidationError("Order is delivered, you can't change the status")
        return attrs

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status')
        instance.save()

        return instance


class OrderListSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
