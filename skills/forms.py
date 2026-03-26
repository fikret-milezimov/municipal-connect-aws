from django import forms
from .models import Skill


class SkillCreateForm(forms.ModelForm):
    class Meta:
        model = Skill
        exclude = ["created_at", "slug", "user"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Guitar lessons",
                                           "class": "form-control"}),
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "What you can teach or offer, schedule, and details"}
            ),
            "contact_name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "contact_phone": forms.TextInput(attrs={"placeholder": "10-digit phone number"}),
        }
