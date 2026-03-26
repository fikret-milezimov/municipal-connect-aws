from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from .forms import RegisterForm
from .models import Profile
from django.contrib.auth.mixins import LoginRequiredMixin

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Your account was created successfully. You can now log in."
        )

        return response





class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("common:home")


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "accounts/profile-details.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        return self.request.user.profile


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ["bio", "location", "profile_picture"]
    template_name = "accounts/profile-edit.html"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return self.request.user.profile

class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "accounts/profile-delete.html"
    success_url = reverse_lazy("common:home")

    def get_object(self, queryset=None):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Your profile was deleted successfully.")
        return super().delete(request, *args, **kwargs)