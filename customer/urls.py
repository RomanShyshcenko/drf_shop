from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views


urlpatterns = [
    path('user/create/', views.RegisterClientView.as_view(), name='create_user'),
    path('user/get/', views.RetrieveUserView.as_view(), name='get_user'),
    path('user/update/', views.UpdateUserView.as_view(), name='update_user'),
    path('user/delete', views.DestroyUserView.as_view(), name='delete_user_and_all_relationship'),

    path('user/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('user/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

    path('user/email/send-verification/', views.SendEmailVerification.as_view(), name='send_email_verification'),
    path('user/email/verification/', views.EmailVerification.as_view(), name='email_verification'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
