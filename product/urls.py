from django.urls import path
from product import views

urlpatterns = [
    path('category/create/', views.CreateCategory.as_view(), name='create_category'),
    path(
        'category/disable/',
        views.CategoryDisableSubcategoriesView.as_view(),
        name='disable_category_and_subcategories'
    ),
    path('sub_category/create/', views.CreateSubCategory.as_view(), name='create_sub_category')

]
