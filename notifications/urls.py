from django.urls import path
from .views import NotificationListView, mark_as_read, NotificationDeleteView, UserNotificationsView

app_name = "notifications"
urlpatterns = [
    path("", NotificationListView.as_view(), name="list"),
    path("<int:pk>/read/", mark_as_read, name="read"),
    path("<int:pk>/delete/", NotificationDeleteView.as_view(), name="delete"),
    path("profile/", UserNotificationsView.as_view(), name="profile-notifications"),
]
