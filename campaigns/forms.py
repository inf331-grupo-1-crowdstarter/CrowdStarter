from decimal import Decimal
import json

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Campaign, Category, Comment

CATEGORY_SUBCATEGORIES = {
    "Tecnología e Innovación": (
        "Tecnología de Consumo", "Hardware y Software", "Impresión 3D y Robótica",
    ),
    "Arte y Cultura": (
        "Cine y Video", "Música", "Publicación y Literatura", "Artes Visuales", "Teatro",
    ),
    "Entretenimiento y Juegos": ("Juegos", "Experiencias Interactivas", "Cómics"),
    "Diseño y Estilo de Vida": ("Moda", "Diseño de Productos", "Gastronomía"),
    "Negocios, Finanzas e Impacto": ("Emprendimiento", "Finanzas", "Innovación Social"),
    "Causas Sociales y Comunidad": ("Medioambiente", "Educación", "Comunidad"),
}


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Correo electrónico"
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmar contraseña"
        for field in self.fields.values():
            field.help_text = ""
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["placeholder"] = field.label

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
            attrs={"autocomplete": "email", "class": "form-control", "placeholder": "Correo electrónico"}
        ),
    )

    error_messages = {
        "invalid_login": "Correo o contraseña incorrectos.",
        "inactive": "Esta cuenta está inactiva.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Correo electrónico"
        self.fields["password"].label = "Contraseña"
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Contraseña", "autocomplete": "current-password"}
        )



class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ["title", "description", "category", "image", "funding_goal", "deadline"]
        labels = {"title": "Título", "description": "Descripción", "category": "Categoría",
                  "image": "Imagen (JPG/PNG, máximo 2 MB)", "funding_goal": "Meta", "deadline": "Fecha límite"}
        widgets = {"deadline": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        category_name = self.instance.category.name if self.instance.pk else ""
        category_id = self.data.get("category") if self.is_bound else None
        if category_id:
            category_name = Category.objects.filter(pk=category_id).values_list("name", flat=True).first() or ""
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control rounded-xl"
            field.widget.attrs["placeholder"] = field.label
        self.fields["description"].widget.attrs.update({"rows": 5, "placeholder": "Describe tu idea y el impacto que buscas..."})
        self.fields["category"].widget.attrs["data-subcategories"] = json.dumps(CATEGORY_SUBCATEGORIES, ensure_ascii=False)

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
                                widget=forms.NumberInput(attrs={"class": "form-control rounded-xl", "step": "0.01", "placeholder": "Monto del aporte"}))


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
