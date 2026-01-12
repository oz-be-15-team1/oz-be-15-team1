from django.urls import path

from .views import (
    SocialTokenView,
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
    path("social/token/", SocialTokenView.as_view(), name="member-social-token"),
]
