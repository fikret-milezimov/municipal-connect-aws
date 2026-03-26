from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect

from common.mixins import SearchMixin
from .forms import MarketplaceCreateForm
from .models import MarketplaceItem


class MarketplaceListView(SearchMixin, ListView):
    model = MarketplaceItem
    template_name = "marketplace/marketplace-list.html"
    context_object_name = "items"
    search_fields = ["title", "description"]

class MarketplaceDetailView(DetailView):
    model = MarketplaceItem
    template_name = "marketplace/marketplace-details.html"
    context_object_name = "item"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.kwargs.get("slug") != self.object.slug:
            return redirect("marketplace:details", pk=self.object.pk, slug=self.object.slug)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

class MarketplaceCreateView(CreateView):
    model = MarketplaceItem
    form_class = MarketplaceCreateForm
    template_name = "marketplace/marketplace-create.html"
    success_url = reverse_lazy("marketplace:list")

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Marketplace item created successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

class MarketplaceUpdateView(UpdateView):
    model = MarketplaceItem
    form_class = MarketplaceCreateForm
    template_name = "marketplace/marketplace-edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.warning(self.request, "Marketplace item updated.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("marketplace:details", kwargs={"pk": self.object.pk, "slug": self.object.slug})

class MarketplaceDeleteView(DeleteView):
    model = MarketplaceItem
    template_name = "marketplace/marketplace-delete.html"
    success_url = reverse_lazy("marketplace:list")

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.warning(self.request, "Marketplace item deleted.")
        return response

class MyItemsListView(LoginRequiredMixin, SearchMixin, ListView):
    model = MarketplaceItem
    template_name = "marketplace/my-items.html"
    context_object_name = "items"
    search_fields = ["title", "description"]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)
