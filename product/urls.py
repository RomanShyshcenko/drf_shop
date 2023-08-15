from django.urls import path
from product import views

urlpatterns = [
    path('category/create/', views.CreateCategory.as_view(), name='create_category'),
    path('category/disable/', views.CategoryDisableSubcategoriesView.as_view(),
         name='disable_category_and_subcategories'),
    path(
        'category/enable/without_subcategories/',
        views.ActivateCategoryWithoutSubCategoriesView.as_view(),
        name='enable_category_without_subcategories'
    ),
    path('sub_category/create/', views.CreateSubCategory.as_view(), name='create_sub_category'),
    path('sub_category/disable/', views.DisableSubCategoryView.as_view(), name='disable_sub_category'),
    path('sub_category/enable/', views.ActivateSubCategoryView.as_view(), name='enable_sub_category'),
    path(
        'sub_category/eneble/all/',
        views.ActivateSubCategoriesOfConcreteCategoryView.as_view(),
        name='activate_sub_categories_of_concrete_category'
    ),

]
