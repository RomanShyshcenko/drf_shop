from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from product.models import Product


def get_product_by_id(product_id):
    try:
        product_id = int(product_id)
        if product_id:
            return get_object_or_404(Product, id=product_id)
        raise ValidationError('Product id must be given')

    except (ValueError, TypeError):
        raise ValidationError({
            'error': {'id': 'You should give a number!'}
        })

