from django import forms
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
            "image": forms.FileInput(attrs={
                "class": "form-control"
            })
        }
