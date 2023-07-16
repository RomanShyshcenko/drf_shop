from django.db import models


class Category(models.Model):
    name = models.CharField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"category{self.name}, is_active={self.is_active}"

    class Meta:
        ordering = ('-created_at', )
        db_table = "category"


class SubCategory(models.Model):
    category_id = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name="sub_category"
    )
    name = models.CharField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"sub_category={self.name}, parent_category={self.category_id.name}, is_active={self.is_active}"

    class Meta:
        ordering = ('-created_at',)
        db_table = "sub_category"


class Product(models.Model):
    name = models.CharField(max_length=155)
    brand = models.CharField(max_length=155)
    description = models.TextField(max_length=1000)
    category_id = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE,
        related_name="products"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created_at', )
        db_table = "product"



# // Use DBML to define your database structure
# // Docs: https://dbml.dbdiagram.io/docs
#
# Table users {
#   id integer
#   uuid uuid [primary key]
#   email varchar
#   first_name varchar
#   last_name varchar
#   password varchar
#   is_staff boolean
#   is_active boolean
#   is_confirmed_email boolean
#   created_at timestamp
#   updated_at timestamp
# }
#
# Table phone_number {
#   id integer [primary key]
#   user_id uuid
#   phone_number varchar
#   is_verified boolean
#   sent timestamp
#   created_at timestamp
#   updated_at timestamp
# }
#
# Table user_address {
#   id integer [primary key]
#   user_id uuid
#   city varchar
#   street_address varchar
#   apartment_address varchar
#   postal_code varchar
#   created_at timestamp
#   updated_at timestamp
# }
#
# Table category {
#   id integer [primary key]
#   name varchar
#   is_active boolean
#   created_at timestamp
# }
#
# Table sub_category{
#   id integer [primary key]
#   category_id integer
#   name varchar
#   is_active boolean
#   created_at timestamp
# }
#
# Table product {
#   id integer [primary key]
#   sub_category_id integer
#   name varchar
#   brand varchar
#   descripption text
#   is_active boolean
#   created_at timestamp
#   updated_at timestamp
#   deleted_at timestamp
# }
#
#
# Ref: "users"."uuid" < "phone_number"."user_id"
#
#
# Ref: "users"."uuid" < "user_address"."user_id"
#
# Ref: "category"."id" < "sub_category"."category_id"
#
# Ref: "sub_category"."id" < "product"."sub_category_id"