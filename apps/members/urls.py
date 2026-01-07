from django.urls import path
from .views import UserSignupView, UserLoginView

urlpatterns = [
    path("signup/", UserSignupView.as_view(), name="member-signup"),
    path("login/", UserLoginView.as_view(), name="member-login"),
]