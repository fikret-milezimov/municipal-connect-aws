from django import forms

from common.utils import is_content_manager

from .models import MarketplaceItem


class MarketplaceCreateForm(forms.ModelForm):
    class Meta:
        model = MarketplaceItem
        exclude = ["created_at", "slug", "user"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Used bike in good condition"}),
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Details, condition, pickup info, and price."}
            ),
            "contact_name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "contact_phone": forms.TextInput(attrs={"placeholder": "10-digit phone number"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            full_name = user.get_full_name()
            self.fields["contact_name"].initial = full_name or user.username

            if not is_content_manager(user):
                self.fields["contact_name"].widget.attrs.update(
                    {
                        "class": "form-control",
                        "style": "background-color: #e9ecef; cursor: not-allowed;",
                    }
                )


class MarketplaceUpdateForm(forms.ModelForm):
    created_at = forms.DateTimeField(
        disabled=True,
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control"},
            format="%d-%m-%Y %H:%M",
        ),
    )

    class Meta:
        model = MarketplaceItem
        exclude = ["slug", "user"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["created_at"].initial = self.instance.created_at
            self.fields["contact_name"].initial = self.instance.contact_name

        if user and user.is_authenticated:
            if not is_content_manager(user):
                self.fields["contact_name"].disabled = True
                self.fields["contact_name"].widget.attrs.update(
                    {
                        "class": "form-control",
                        "style": "background-color: #e9ecef;",
                    }
                )
