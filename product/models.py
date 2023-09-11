from django.db import models


class Category(models.Model):
    name = models.CharField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"category{self.name}, is_active={self.is_active}, id={self.id}"

    class Meta:
        ordering = ('-created_at', )
        db_table = "category"


class SubCategory(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name="sub_category"
    )
    name = models.CharField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"sub_category={self.name}, parent_category={self.category.name}, is_active={self.is_active}"

    class Meta:
        ordering = ('-created_at',)
        db_table = "sub_category"


class Product(models.Model):
    category = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE,
        related_name="products"
    )
    name = models.CharField(max_length=155)
    brand = models.CharField(max_length=155)
    description = models.TextField(max_length=1000)
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Price in UAH', default=0)
    quantity = models.IntegerField(default=1)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created_at', )
        db_table = "product"


