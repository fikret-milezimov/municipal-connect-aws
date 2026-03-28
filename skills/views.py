from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect

from common.mixins import SearchMixin
from common.utils import is_content_manager
from .forms import SkillCreateForm, SkillUpdateForm
from .models import Skill


class SkillListView(SearchMixin, ListView):
    model = Skill
    template_name = "skills/skill-list.html"
    context_object_name = "skills"
    search_fields = ["name", "description"]

class SkillDetailView(DetailView):
    model = Skill
    template_name = "skills/skill-details.html"
    context_object_name = "skill"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.kwargs.get("slug") != self.object.slug:
            return redirect("skills:details", pk=self.object.pk, slug=self.object.slug)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["can_edit"] = (
                self.request.user == self.object.user
                or is_content_manager(self.request.user)
        )

        return context

class SkillCreateView(LoginRequiredMixin, CreateView):
    model = Skill
    form_class = SkillCreateForm
    template_name = "skills/skill-create.html"
    success_url = reverse_lazy("skills:list")

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Skill created successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url
        return reverse_lazy("skills:list")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "You must be logged in to perform this action.")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

class SkillUpdateView(UpdateView):
    model = Skill
    form_class = SkillUpdateForm
    template_name = "skills/skill-edit.html"

    def form_valid(self, form):
        if not is_content_manager(self.request.user):
            form.instance.contact_name = self.get_object().contact_name

        response = super().form_valid(form)
        messages.warning(self.request, "Skill updated.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_success_url(self):
        next_url = self.request.POST.get("next")

        if next_url:
            return next_url

        return reverse_lazy(
            "skills:details",
            kwargs={"pk": self.object.pk, "slug": self.object.slug},
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        qs = super().get_queryset()

        if is_content_manager(self.request.user):
            return qs

        return qs.filter(user=self.request.user)

class SkillDeleteView(DeleteView):
    model = Skill
    template_name = "skills/skill-delete.html"

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "Skill deleted.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.POST.get("next") or reverse_lazy("skills:list")

    def get_queryset(self):
        qs = super().get_queryset()

        if is_content_manager(self.request.user):
            return qs

        return qs.filter(user=self.request.user)

class MySkillsListView(LoginRequiredMixin, SearchMixin, ListView):
    model = Skill
    template_name = "skills/my-skills.html"
    context_object_name = "skills"
    search_fields = ["name", "description"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)
