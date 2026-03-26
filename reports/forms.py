from django import forms
from .models import Report


class ReportCreateForm(forms.ModelForm):
    class Meta:
        model = Report
        exclude = ["created_at", "slug", "user"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Broken streetlight"}),
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Describe the issue"}
            ),
            "location": forms.TextInput(attrs={"placeholder": "123 Dondukov Blv, near the park entrance"}),
            "contact_name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "contact_phone": forms.TextInput(attrs={"placeholder": "10-digit phone number"}),
        }

class ReportUpdateForm(forms.ModelForm):
    created_at = forms.DateTimeField(
        disabled=True,
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control"},
            format="%d-%m-%Y %H:%M"
        )
    )
    class Meta:
        model = Report
        exclude = ["slug", "user"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["created_at"].initial = self.instance.created_at
