from django import forms

from common.utils import is_moderator
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
            "contact_phone": forms.TextInput(attrs={"placeholder": "10-digit phone number"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:

            self.fields["contact_name"].initial = user.get_full_name()

            if not user.groups.filter(name="Moderators").exists():
                self.fields["contact_name"].widget.attrs.update({
                    "class": "form-control",
                    "style": "background-color: #e9ecef; cursor: not-allowed;"
                })

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
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["created_at"].initial = self.instance.created_at

        is_mod = user and user.groups.filter(name="Moderators").exists()


        if not is_mod:
            self.fields["status"].disabled = True
            self.fields["status"].widget.attrs.update({
                "class": "form-control",
                "style": "background-color: #e9ecef;"
            })


        if user and user.is_authenticated:
            full_name = user.get_full_name()
            self.fields["contact_name"].initial = full_name or user.username

            if not is_mod:
                self.fields["contact_name"].disabled = True
                self.fields["contact_name"].widget.attrs.update({
                    "class": "form-control",
                    "style": "background-color: #e9ecef;"
                })