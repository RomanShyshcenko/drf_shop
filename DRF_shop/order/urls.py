from django.urls import path, re_path

from order import views

urlpatterns = [
    path('order/create/', views.CreateOrderAPIView.as_view(), name='order_create'),
    path('order/update-status/', views.UpdateOrderStatusAPIView.as_view(), name='order_status_update'),
    path('order/all/', views.GetOrdersListAPIView.as_view(), name='order_all'),  # all orders of concrete user
    path('order/details/', views.GetOrderAPIView.as_view(), name='order_details'),
]
