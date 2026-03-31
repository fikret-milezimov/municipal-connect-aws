from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView
from urllib.parse import urlencode
from .models import Notification


class UserNotificationsQuerysetMixin:
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")


class NotificationListView(LoginRequiredMixin, UserNotificationsQuerysetMixin, ListView):
    model = Notification
    template_name = "notifications/profile-notifications.html"


@login_required
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    next_url = request.GET.get("next") or "notifications:profile-notifications"
    return_to = request.GET.get("return_to")

    if return_to:
        separator = "&" if "?" in next_url else "?"
        next_url = f"{next_url}{separator}{urlencode({'next': return_to})}"

    return redirect(next_url)


class UserNotificationsView(LoginRequiredMixin, UserNotificationsQuerysetMixin, ListView):
    model = Notification
    template_name = "notifications/profile-notifications.html"


class NotificationDeleteView(LoginRequiredMixin, DeleteView):
    model = Notification
    template_name = "notifications/notification-delete.html"

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_success_url(self):
        return self.request.POST.get("next") or reverse_lazy("notifications:profile-notifications")

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.warning(self.request, "Notification deleted.")
        return response
