from django.urls import path
from .views import RegisterView, UserLoginView, UserLogoutView, ProfileDetailView, ProfileUpdateView, ProfileDeleteView

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("profile/", ProfileDetailView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile-edit"),
    path("profile/delete/", ProfileDeleteView.as_view(), name="profile-delete"),
]