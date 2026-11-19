from decimal import Decimal

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Campaign, Comment


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")

    class Meta:
        model = User
        fields = ["email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"].lower()
        user.email = self.cleaned_data["email"].lower()

        if commit:
            user.save()

        return user

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={"autocomplete": "email"}
        ),
    )

    error_messages = {
        "invalid_login": "Correo o contraseña incorrectos.",
        "inactive": "Esta cuenta está inactiva.",
    }



class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ["title", "description", "category", "image", "funding_goal", "deadline"]
        labels = {"title": "Título", "description": "Descripción", "category": "Categoría",
                  "image": "Imagen (JPG/PNG, máximo 2 MB)", "funding_goal": "Meta", "deadline": "Fecha límite"}
        widgets = {"deadline": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_funding_goal(self):
        goal = self.cleaned_data["funding_goal"]
        if goal <= 0:
            raise forms.ValidationError("La meta debe ser mayor a cero.")
        if self.instance.pk and goal < self.instance.raised_amount:
            raise forms.ValidationError("La meta no puede ser inferior al monto recaudado.")
        return goal

    def clean_deadline(self):
        deadline = self.cleaned_data["deadline"]
        today = timezone.localdate()
        if deadline < today or (not self.instance.pk and deadline == today):
            raise forms.ValidationError("La fecha límite debe ser futura al crear y no pasada al editar.")
        return deadline

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and hasattr(image, "content_type"):
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError("La imagen no puede superar 2 MB.")
            if image.image.format not in {"JPEG", "PNG"} or image.name.rsplit(".", 1)[-1].lower() not in {"jpg", "jpeg", "png"}:
                raise forms.ValidationError("Solo se permiten imágenes JPG o PNG.")
        return image


class ContributionForm(forms.Form):
    amount = forms.DecimalField(label="Monto del aporte simulado", max_digits=12, decimal_places=2,
                                min_value=Decimal("0.01"),
                                widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}))


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label="Tu comentario", max_length=1000, strip=True,
        help_text="Máximo 1.000 caracteres.",
        error_messages={"required": "Escribe un comentario; no puede contener solo espacios.",
                        "max_length": "El comentario no puede superar 1.000 caracteres."},
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "maxlength": 1000}),
    )

    class Meta:
        model = Comment
        fields = ["content"]
