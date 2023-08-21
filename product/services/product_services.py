from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound

from product.models import Product


def get_product_by_id(product_id):
    try:
        if product_id:
            return Product.objects.get(id=product_id)
        raise ValidationError(code=status.HTTP_400_BAD_REQUEST)
    except Product.DoesNotExist:
        raise NotFound(detail="Product doesn't exist!")
