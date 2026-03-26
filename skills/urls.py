from django.urls import path
from .views import SkillListView, SkillDetailView, SkillCreateView, SkillUpdateView, SkillDeleteView, MySkillsListView

app_name = "skills"

urlpatterns = [
    path("", SkillListView.as_view(), name="list"),
    path("my-skills/", MySkillsListView.as_view(), name="my-skills"),
    path("create/", SkillCreateView.as_view(), name="create"),
    path("<int:pk>-<slug:slug>/", SkillDetailView.as_view(), name="details"),
    path("<int:pk>/edit/", SkillUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", SkillDeleteView.as_view(), name="delete"),
]
