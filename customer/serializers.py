from rest_framework import serializers
from django.core.validators import MinValueValidator
from rest_framework import status
from backend.customer.models import User, UserAddress
from django.contrib.auth.hashers import check_password


class UserAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAddress
        fields = ('city', 'street_address', 'apartment_address', 'postal_code')


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False)
    is_verified = serializers.BooleanField()


class RetrieveUserSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField(read_only=True)
    is_confirmed_email = serializers.BooleanField(read_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone_number = PhoneNumberSerializer()
    address = UserAddressSerializer()


class RegisterUserSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=120)
    password = serializers.CharField(
        max_length=55, validators=[MinValueValidator],
    )
    confirm_password = serializers.CharField(
        validators=[MinValueValidator], max_length=55,
        required=False
    )

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Pleas enter your password correct 2 times')
        return data

    def create(self, validated_data):
        try:
            user = User.objects.create_user(
                email=validated_data['email'],
            ).set_password(
                validated_data['password']
            )
        except Exception as e:
            raise serializers.ValidationError(detail={"massage": "User already exist", "error": e},
                                              code=status.HTTP_400_BAD_REQUEST)
        return user


class UpdateFirstOrLastNameUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        new_password = data['new_password']
        old_password = self.instance.password
        if len(new_password) < 8:
            raise serializers.ValidationError("new password length mast be > 8")

        elif not check_password(data['old_password'], old_password):
            raise serializers.ValidationError('Pleas correctly enter your old password')

        elif check_password(new_password, old_password):
            raise serializers.ValidationError('New password cannot match old')

        elif new_password != data['confirm_password']:
            raise serializers.ValidationError("Passwords doesn't match")
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get('new_password'))
        instance.save()
        return instance


class UpdateUserEmaiSerializer(serializers.Serializer):
    email = serializers.EmailField()
