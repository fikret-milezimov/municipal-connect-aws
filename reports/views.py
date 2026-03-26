from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect

from common.mixins import SearchMixin
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

class ReportCreateView(CreateView):
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

class ReportUpdateView(UpdateView):
    model = Report
    form_class = ReportUpdateForm
    template_name = "reports/report-edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.warning(self.request, "Report updated.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("reports:details", kwargs={"pk": self.object.pk, "slug": self.object.slug})

class ReportDeleteView(DeleteView):
    model = Report
    template_name = "reports/report-delete.html"
    success_url = reverse_lazy("reports:list")

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.warning(self.request, "Report deleted.")
        return response





class MyReportsListView(LoginRequiredMixin, SearchMixin, ListView):
    model = Report
    template_name = "reports/my-reports.html"
    context_object_name = "reports"
    search_fields = ["title", "description", "location"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)