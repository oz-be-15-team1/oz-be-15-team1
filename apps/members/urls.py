from django.urls import path

from .views import (
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    UserSignupView,
)

urlpatterns = [
    path("signup/", UserSignupView.as_view(), name="member-signup"),
    path("login/", UserLoginView.as_view(), name="member-login"),
    path("logout/", UserLogoutView.as_view(), name="member-logout"),
    path("profile/", UserProfileView.as_view(), name="member-profile"),
]
