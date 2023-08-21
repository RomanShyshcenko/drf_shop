from django.urls import path
from product import views

urlpatterns = [
    # Product
    path('product/create/', views.CreateProductView.as_view(), name='create_product'),
    path('product/update/', views.UpdateProductView.as_view(), name='update_product'),
    path('product/is_active/', views.IsActivaStatusProductView.as_view(), name='is_active_status_product'),
    path('product/get/', views.GetProduct.as_view(), name='product_detail'),
    # Category
    path('category/create/', views.CreateCategory.as_view(), name='create_category'),
    path('category/disable/', views.CategoryDisableSubcategoriesView.as_view(),
         name='disable_category_and_subcategories'),
    path('category/enable/', views.ActivateCategoryView.as_view(), name='enable_category'),
    # path('category/get/', views.GetCategoryView.as_view(), name='get_category'),
    # Sub category
    path('sub_category/create/', views.CreateSubCategory.as_view(), name='create_sub_category'),
    path('sub_category/disable/', views.DisableSubCategoryView.as_view(), name='disable_sub_category'),
    path('sub_category/enable/', views.ActivateSubCategoryView.as_view(), name='enable_sub_category'),
    path('sub_category/enable/all/',
         views.ActivateSubCategoriesOfConcreteCategoryView.as_view(),
         name='activate_sub_categories_of_concrete_category'
         ),
    # path('sub_category/get/', views.GetSubCategoryView.as_view(), name='get_sub_category'),
]
