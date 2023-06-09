from rest_framework import serializers
from django.core.validators import MinValueValidator
from rest_framework import status
from customer.models import User, UserAddress, password_regex


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
        max_length=55, validators=[password_regex],
    )
    confirm_password = serializers.CharField(
        validators=[password_regex], max_length=55,
        write_only=True, required=True
    )

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Pleas confirm your password")
        return data

    def create(self, validated_data):
        try:
            user = User.objects.create_user(
                email=validated_data.pop('email'),
                password=validated_data.pop('password')
            )
        except Exception as e:
            raise serializers.ValidationError(
                detail={"massage": "User already exist", "error": e},
                code=status.HTTP_400_BAD_REQUEST
            )
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


class UpdateUserEmaiSerializer(serializers.Serializer):
    email = serializers.EmailField()
