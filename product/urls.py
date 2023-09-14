from django.urls import path
from product import views

urlpatterns = [
    # Product
    path('product/create/', views.CreateProductView.as_view(), name='create_product'),
    path('product/update/', views.UpdateProductView.as_view(), name='update_product'),
    path('product/is_active/', views.IsActivaStatusProductView.as_view(), name='is_active_status_product'),
    path('product/detail/', views.GetProduct.as_view(), name='product_detail'),
    path('product/', views.ProductsListAPIView.as_view(), name='list_of_products'),
    # Category
    path('category/create/', views.CreateCategory.as_view(), name='create_category'),
    path('category/update-status/', views.UpdateStatusCategoryView.as_view(), name='update_status_category'),
    path('category/all/', views.GetCategoryListView.as_view(), name='get_category'),
    path('sub_category/create/', views.CreateSubCategory.as_view(), name='create_sub_category'),
    path('sub_category/update-status/', views.UpdateStatusSubCategoryView.as_view(), name='update_status_sub_category'),
    path('sub_category/enable/all/',
         views.ActivateSubCategoriesOfConcreteCategoryView.as_view(),
         name='activate_sub_categories_of_concrete_category'
         ),
]
