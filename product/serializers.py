from django.utils import timezone
from rest_framework.serializers import ModelSerializer, Serializer

from product.models import Product, Category, SubCategory


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'category_id', 'name', 'brand', 'description', 'is_active',
                  'created_at', 'updated_at', 'deleted_at')
        read_only_fields = ('id', 'category_id', 'created_at')

    def create(self, validated_data):
        product = Product.objects.create(
            name=validated_data.get('name'),
            brand=validated_data.get('brand'),
            description=validated_data.get('description'),
            category_id=validated_data.get('category_id')
        )

        return product

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.brand = validated_data.get('brand', instance.brand)
        instance.description = validated_data.get('description', instance.description)
        instance.category_id = validated_data.get('category_id', instance.category_id)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.updated_at = timezone.now()
        instance.save()

        return instance


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        category = Category.objects.create(
            name=validated_data.get('name')
        )
        return category


class DisableCategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'is_active')
        read_only_fields = ('id', 'name')

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

