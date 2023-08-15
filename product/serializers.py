from django.utils import timezone
from rest_framework import serializers, status
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


class CategoryActivateSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'is_active')

    def validate(self, attrs):
        if self.instance.is_active:
            raise serializers.ValidationError(
                detail="Category already activated!",
                code=status.HTTP_400_BAD_REQUEST
            )
        return attrs


class CreateSubCategorySerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ('name', 'category_id')

    def create(self, validated_data):
        sub_category = SubCategory.objects.create(
            name=validated_data.get('name'),
            category_id=validated_data.get('category_id')
        )
        return sub_category


class SubCategoryDisableSerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ('id', 'name', 'is_active', 'created_at')
        read_only_fields = ('id', 'name')

    def validate(self, attrs):
        if not self.instance.is_active:
            raise serializers.ValidationError(
                detail="Sub category already disabled!",
                code=status.HTTP_400_BAD_REQUEST
            )
        return attrs

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance


class SubCategoryActivateSerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ('id', 'name', 'is_active', 'created_at')
        read_only_fields = ('id', 'name')

    def validate(self, attrs):
        parent_cat = Category.objects.get(id=self.instance.category_id.id)
        if not parent_cat.is_active:
            raise serializers.ValidationError(
                detail="You can't activate sub category with deactivated parent category",
                code=status.HTTP_400_BAD_REQUEST
            )
        if self.instance.is_active:
            raise serializers.ValidationError(
                detail="Category already active!"
            )
        return attrs

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance


class ActivateSubCategoriesOfConcreteCategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'is_active')
        read_only_fields = ('id', 'name')

    def validate(self, attrs):
        if not self.instance.is_active:
            raise serializers.ValidationError(
                detail={
                    'message': 'Parent category deactivated!. '
                               'Pleas enable parent category.'
                },
                code=status.HTTP_400_BAD_REQUEST
            )
        return attrs

    def update(self, instance, validated_data):
        SubCategory.objects.filter(
            category_id=instance.id,
            is_active=False
        ).update(is_active=True)

        sub_categories = SubCategory.objects.filter(
            category_id=instance.id,
            is_active=True
        )

        sub_categories_list = [{'name': sub_cat.name, 'is_active': sub_cat.is_active} for sub_cat in sub_categories]

        return {
            'parent_category': instance.name,
            'sub_categories': sub_categories_list
        }


