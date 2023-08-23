from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.serializers import ModelSerializer

from product.models import Product, Category, SubCategory


class CreateProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id', 'category_id', 'name', 'brand', 'price',
            'quantity', 'description', 'is_active', 'created_at'
        )
        read_only_fields = ('id', 'created_at')

    def validate(self, attrs):
        cat_id = attrs.get('category_id').id
        if type(cat_id) != int:
            raise serializers.ValidationError(
                code=status.HTTP_400_BAD_REQUEST,
                detail={'error': {'category_id': f'You should give a number!'}}
            )
        try:
            SubCategory.objects.get(id=cat_id)
        except SubCategory.DoesNotExist:
            raise serializers.ValidationError(
                code=status.HTTP_400_BAD_REQUEST,
                detail={'message': f'Category with id: {cat_id} does not exist!'}
            )
        return attrs

    def create(self, validated_data):
        product = Product.objects.create(
            name=validated_data.get('name'),
            brand=validated_data.get('brand'),
            price=validated_data.get('price'),
            quantity=validated_data.get('quantity'),
            description=validated_data.get('description'),
            category_id=validated_data.get('category_id')
        )
        product = {
            "id": product.id,
            "category_id": product.category_id,
            "name": product.name,
            "brand": product.brand,
            "price": product.price,
            "quantity": product.quantity,
            "description": product.description,
            "is_active": product.is_active,
            "created_at": product.created_at
        }
        return product


class GetProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id', 'category_id', 'name', 'brand', 'price',
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

        product = {
            "id": instance.id,
            "category_id": {
                'id': instance.category_id.id,
                'name': instance.category_id.name
            },
            "name": instance.name,
            "brand": instance.brand,
            "price": instance.price,
            "quantity": instance.quantity,
            "description": instance.description,
            "is_active": instance.is_active,
            "created_at": instance.created_at
        }
        return product


class IsActiveStatusProductSerializer(ModelSerializer):

    class Meta:
        model = Product
        fields = ('id', 'name', 'brand', 'price', 'description', 'is_active', 'updated_at', 'deleted_at')
        read_only_fields = ('id', 'name', 'brand', 'price', 'description', 'updated_at')

    def validate(self, attrs):
        is_active = attrs.get('is_active')
        if type(is_active) != bool:
            raise serializers.ValidationError(
                code=status.HTTP_400_BAD_REQUEST,
                detail={'error': {'category_id': f'You should give a boolean type!'}}
            )
        if is_active and self.instance.is_active:
            raise serializers.ValidationError(
                detail="Product already activated!"
            )
        if not is_active and not self.instance.is_active:
            raise serializers.ValidationError(
                detail="Product already deactivated!"
            )
        return attrs

    def update(self, instance, validated_data):
        is_active = validated_data.get('is_active')
        if is_active:
            instance.is_active = is_active
            instance.save()
        if not is_active:
            instance.is_active = is_active
            instance.deleted_at = timezone.now()
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
        # Task:
        # It should disable all products depends on this sub category.
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


