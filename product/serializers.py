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
        if not isinstance(cat_id, int):
            raise serializers.ValidationError(
                {'error': {'category_id': f'You should give a number!'}}
            )
        try:
            SubCategory.objects.get(id=cat_id)
        except SubCategory.DoesNotExist:
            raise serializers.ValidationError(
                {'message': f'Category with id: {cat_id} does not exist!'}

            )
        return attrs

    def create(self, validated_data):
        product = Product.objects.create(**validated_data)
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


class CategoryActivateSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'is_active')

    def validate(self, attrs):
        if self.instance.is_active:
            raise serializers.ValidationError("Category already activated!")
        return attrs


class CreateSubCategorySerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ('name', 'category_id')

    def create(self, validated_data):
        sub_category = SubCategory.objects.create(**validated_data)
        return sub_category


class SubCategoryDisableSerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ('id', 'name', 'is_active', 'created_at')
        read_only_fields = ('id', 'name')

    def validate(self, attrs):
        if not self.instance.is_active:
            raise serializers.ValidationError("Sub category already disabled!")

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
        # Retrieve the parent category
        parent_cat = Category.objects.get(id=self.instance.category_id.id)

        # Check if the parent category is active
        if not parent_cat.is_active:
            raise serializers.ValidationError(
                "You can't activate sub category with deactivated parent category",
                status.HTTP_400_BAD_REQUEST)

        # Check if the subcategory is already active
        if self.instance.is_active:
            raise serializers.ValidationError(detail="Category already active!")

        return attrs

    def update(self, instance, validated_data):
        # Update the is_active field
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
            raise serializers.ValidationError({
                'message': 'Parent category deactivated!. Pleas enable parent category.'
            })

        return attrs

    def update(self, instance, validated_data):
        # Activate inactive subcategories
        SubCategory.objects.filter(category_id=instance.id,
                                   is_active=False).update(is_active=True)
        # Fetch and serialize activated subcategories
        sub_categories = SubCategory.objects.filter(category_id=instance.id, is_active=True)
        sub_categories_list = [{'name': sub_cat.name, 'is_active': sub_cat.is_active}
                               for sub_cat in sub_categories]

        return {
            'parent_category': instance.name,
            'sub_categories': sub_categories_list
        }


