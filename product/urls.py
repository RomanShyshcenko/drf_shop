from django.urls import path
from product.views import CreateCategory, DisableCategory

urlpatterns = [
    path('category/create/', CreateCategory.as_view(), name='create_category'),
    path('category/disable/', DisableCategory.as_view(), name='disable_category'),
]
