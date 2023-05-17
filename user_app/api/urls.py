from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from user_app.api.views import (
    RegisterView,
    ResetPasswordEmailView,
    ResetPasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "user/reset-password/email/",
        ResetPasswordEmailView.as_view(),
        name="reset-password-email",
    ),
    path(
        "user/reset-password/<uid>/<token>/",
        ResetPasswordView.as_view(),
        name="reset-password-confirm",
    ),
    path("user/login/", TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("user/login/refresh/", TokenRefreshView.as_view(), name='token_refresh'),
]
