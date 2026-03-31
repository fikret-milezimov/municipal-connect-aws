from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect

from common.mixins import SearchMixin
from common.utils import is_moderator
from .models import Report
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import ReportCreateForm, ReportUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView




class ReportListView(SearchMixin, ListView):
    model = Report
    template_name = "reports/report-list.html"
    context_object_name = "reports"
    search_fields = ["title", "description"]

class ReportDetailView(DetailView):
    model = Report
    template_name = "reports/report-details.html"
    context_object_name = "report"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.kwargs.get("slug") != self.object.slug:
            return redirect("reports:details", pk=self.object.pk, slug=self.object.slug)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["is_moderator"] = is_moderator(self.request.user)
        context["can_edit"] = (
                self.request.user == self.object.user
                or context["is_moderator"]
        )

        return context

class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    form_class = ReportCreateForm
    template_name = "reports/report-create.html"
    success_url = reverse_lazy("reports:list")

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Report created successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url
        return reverse_lazy("reports:list")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "You must be logged in to perform this action.")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

class ReportUpdateView(UpdateView):
    model = Report
    form_class = ReportUpdateForm
    template_name = "reports/report-edit.html"

    def form_valid(self, form):
        is_mod = is_moderator(self.request.user)  # 🔥 извикваш функцията
        print("IS MODERATOR:", is_moderator)
        print("USER:", self)

        if not is_mod:
            obj = self.get_object()
            form.instance.status = obj.status
            form.instance.contact_name = obj.contact_name

        response = super().form_valid(form)
        messages.warning(self.request, "Report updated.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_success_url(self):
        next_url = self.request.POST.get("next")
        if next_url:
            return next_url
        return reverse_lazy("reports:details", kwargs={"pk": self.object.pk, "slug": self.object.slug})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        qs = super().get_queryset()

        if is_moderator(self.request.user):
            return qs

        return qs.filter(user=self.request.user)


class ReportDeleteView(DeleteView):
    model = Report
    template_name = "reports/report-delete.html"
    success_url = reverse_lazy("reports:list")

    def get_success_url(self):
        return self.request.POST.get("next") or reverse_lazy("reports:list")

    def get_queryset(self):
        qs = super().get_queryset()

        if is_moderator(self.request.user):
            return qs

        return qs.filter(user=self.request.user)

    def form_valid(self, form):
        messages.warning(self.request, "Report deleted.")
        return super().form_valid(form)





class MyReportsListView(LoginRequiredMixin, SearchMixin, ListView):
    model = Report
    template_name = "reports/my-reports.html"
    context_object_name = "reports"
    search_fields = ["title", "description", "location"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)
