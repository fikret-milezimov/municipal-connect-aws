from django.urls import path

from reports.api.views import ReportListCreateAPIView, ReportRetrieveUpdateDestroyAPIView


urlpatterns = [
    path("", ReportListCreateAPIView.as_view(), name="report-api-list-create"),
    path("<int:pk>/", ReportRetrieveUpdateDestroyAPIView.as_view(), name="report-api-detail"),
]
