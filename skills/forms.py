from django import forms

from common.utils import is_content_manager

from .models import Skill


class SkillCreateForm(forms.ModelForm):
    class Meta:
        model = Skill
        exclude = ["created_at", "slug", "user"]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Guitar lessons", "class": "form-control"}
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "What you can teach or offer, schedule, and details",
                }
            ),
            "contact_name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "contact_phone": forms.TextInput(attrs={"placeholder": "10-digit phone number"}),
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


class SkillUpdateForm(forms.ModelForm):
    created_at = forms.DateTimeField(
        disabled=True,
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control"},
            format="%d-%m-%Y %H:%M",
        ),
    )

    class Meta:
        model = Skill
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
