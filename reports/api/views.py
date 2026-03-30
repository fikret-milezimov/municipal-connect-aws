from rest_framework import generics, permissions

from common.utils import is_moderator
from reports.api.serializers import ReportSerializer
from reports.models import Report


class IsOwnerOrModeratorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        return obj.user == request.user or is_moderator(request.user)


class ReportListCreateAPIView(generics.ListCreateAPIView):

    queryset = Report.objects.select_related("user").all()
    serializer_class = ReportSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReportRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Report.objects.select_related("user").all()
    serializer_class = ReportSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrModeratorOrReadOnly,
    )
