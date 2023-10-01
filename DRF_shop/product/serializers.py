from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from product.models import Product, Category, SubCategory


class CreateProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id', 'category', 'name', 'brand', 'price',
            'quantity', 'description', 'is_active', 'created_at'
        )
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        product = Product.objects.create(**validated_data)
        return product


class GetProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id', 'category', 'name', 'brand', 'price',
            'quantity', 'description', 'is_active', 'created_at'
        )
        read_only_fields = fields


class UpdateProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'brand', 'price', 'quantity', 'description')
        read_only_fields = ('id', 'created_at')

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.brand = validated_data.get('brand', instance.brand)
        instance.price = validated_data.get('price', instance.price)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        return instance


class IsActiveStatusProductSerializer(ModelSerializer):

    class Meta:
        model = Product
        fields = ('id', 'name', 'brand', 'price', 'description', 'is_active', 'updated_at', 'deleted_at')
        read_only_fields = ('id', 'name', 'brand', 'price', 'description', 'updated_at')

    def validate(self, attrs):
        is_active = attrs.get('is_active')
        if not isinstance(is_active, bool):
            raise serializers.ValidationError(
                {'error': {'category_id': f'You should give a boolean type!'}}
            )

        if is_active and self.instance.is_active:
            raise serializers.ValidationError("Product already activated!")

        if not is_active and not self.instance.is_active:
            raise serializers.ValidationError("Product already deactivated!")

        return attrs

    def update(self, instance, validated_data):
        is_active = validated_data.get('is_active')
        if is_active:
            instance.is_active = True
            instance.deleted_at = None  # Reset the deleted_at field
        else:
            instance.is_active = False
            instance.deleted_at = timezone.now()

        instance.save()
        return instance


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        category = Category.objects.create(name=validated_data.get('name'))
        return category


class UpdateStatusCategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'is_active')

    def validate(self, attrs):
        is_active = attrs.get('is_active')
        instance_is_active = self.instance.is_active

        if instance_is_active and is_active:
            raise serializers.ValidationError("Category already activated!")
        if not instance_is_active and not is_active:
            raise serializers.ValidationError("Category already disabled!")

        return attrs

    def update(self, instance, validated_data):
        is_active = validated_data.get('is_active')
        instance.is_active = is_active

        if not is_active:
            # disable all active sub categories
            instance.sub_category.filter(is_active=True).update(is_active=is_active)

        instance.save()
        return instance


class CreateSubCategorySerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ('name', 'category')

    def create(self, validated_data):
        sub_category = SubCategory.objects.create(**validated_data)
        return sub_category


class UpdateStatusSubCategorySerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ('id', 'name', 'is_active', 'created_at')
        read_only_fields = ('id', 'name')

    def validate(self, attrs):
        is_active = attrs.get('is_active')
        instance_is_active = self.instance.is_active
        parent_cat = self.instance.category

        # Check if the parent category is active
        if is_active and not parent_cat.is_active:
            message = "You can't activate sub category with deactivated parent category"
            raise serializers.ValidationError(message)

        if instance_is_active and is_active:
            message = "Sub category already activated!"
            raise serializers.ValidationError(message)

        if not instance_is_active and not is_active:
            message = "Sub category already disabled!"
            raise serializers.ValidationError(message)

        return attrs

    def update(self, instance, validated_data):
        is_active = validated_data.get('is_active')
        instance.is_active = is_active

        if not is_active:
            instance.products.filter(is_active=True).update(is_active=is_active)

        instance.save()
        return instance


class ActivateSubCategoriesSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'is_active')
        read_only_fields = ('id', 'name')

    def validate(self, attrs):
        if not self.instance.is_active:
            raise serializers.ValidationError({
                'message': 'Parent category deactivated!. Pleas enable parent category.'
            })

        return attrs

    def update(self, instance, validated_data):
        # Activate inactive subcategories
        SubCategory.objects.filter(category=instance.id,
                                   is_active=False).update(is_active=True)
        # Fetch and serialize activated subcategories
        sub_categories = SubCategory.objects.filter(category=instance.id, is_active=True)
        sub_categories_list = [{'name': sub_cat.name, 'is_active': sub_cat.is_active}
                               for sub_cat in sub_categories]

        return {
            'parent_category': instance.name,
            'sub_categories': sub_categories_list
        }


