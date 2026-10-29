from django import forms

from .models import CampaignUpdate


class CampaignUpdateForm(forms.ModelForm):
    title = forms.CharField(
        label="Título", max_length=150, strip=True,
        help_text="Máximo 150 caracteres.",
        error_messages={"required": "Escribe un título; no puede contener solo espacios.",
                        "max_length": "El título no puede superar 150 caracteres."},
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    content = forms.CharField(
        label="Contenido", max_length=5000, strip=True,
        help_text="Máximo 5.000 caracteres.",
        error_messages={"required": "Escribe el contenido; no puede contener solo espacios.",
                        "max_length": "El contenido no puede superar 5.000 caracteres."},
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 6}),
    )

    class Meta:
        model = CampaignUpdate
        fields = ["title", "content"]
