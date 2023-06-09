from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views


urlpatterns = [
    path('user/create/', views.RegisterClientView.as_view(), name='create_user'),
    path('user/get/', views.RetrieveUserView.as_view(), name='get_user'),
    path('user/update/', views.UpdateFirstOrLastNameView.as_view(), name='update_first_last_name'),
    path('user/delete', views.DestroyUserView.as_view(), name='delete_user_and_all_relationship'),

    path('user/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]