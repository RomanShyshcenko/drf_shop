from rest_framework import serializers
from django.contrib.auth import get_user_model

from customer.models import UserAddresses, password_regex

User = get_user_model()


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddresses
        fields = ('city', 'street_address', 'apartment_address', 'postal_code', )


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False)
    is_verified = serializers.BooleanField()

    def update(self, instance, validated_data):
        instance.phone_number = validated_data.get(
            'phone_number', instance.phone_number
        )
        instance.is_verified = False
        instance.save()

        return instance


class UserSerializer(serializers.ModelSerializer):

    phone_number = PhoneNumberSerializer(read_only=True)
    address = UserAddressSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'address', 'phone_number']
        read_only_fields = ['id', 'is_confirmed_email', 'email']

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address')
        address = instance.address  # Get the first Address instance

        # update user data
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        # update address data
        if address_data and address:
            address.city = address_data.get('city', address.city)
            address.street_address = address_data.get('street_address', address.street_address)
            address.apartment_address = address_data.get('apartment_address', address.apartment_address)
            address.postal_code = address_data.get('postal_code', address.postal_code)
            address.save()

        return instance


class RegisterUserSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=120)
    password = serializers.CharField(max_length=55, validators=[password_regex], write_only=True)
    confirm_password = serializers.CharField(
        validators=[password_regex], max_length=55,
        write_only=True, required=True
    )

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User already exists!")
        # You need to return the value in after validation.
        return value

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Pleas confirm your password")
        return data

    def create(self, validated_data):

        user = User.objects.create_user(
            email=validated_data.get('email'),
            password=validated_data.get('password')
        )

        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        max_length=55, write_only=True,
        required=True
    )
    new_password = serializers.CharField(
        validators=[password_regex], max_length=55,
        write_only=True, required=True
    )
    confirm_password = serializers.CharField(
        validators=[password_regex], max_length=55,
        write_only=True, required=True
    )

    def validate(self, data):
        new_password = data.get('new_password')

        if not self.instance.verify_password(data.get('old_password')):
            raise serializers.ValidationError('Pleas correctly enter your old password')

        elif self.instance.verify_password(new_password):
            raise serializers.ValidationError('New password cannot match old')

        elif new_password != data.get('confirm_password'):
            raise serializers.ValidationError("Passwords doesn't match")
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data.pop('new_password'))
        instance.save()
        return instance


class ChangeUserEmaiSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get('email')

        if email == self.instance.email:
            raise serializers.ValidationError("new email can't math old")

        return data

    def update(self, instance, validated_data):
        instance.email = validated_data.pop('email')
        instance.is_confirmed_email = False
        instance.save()
        return instance
