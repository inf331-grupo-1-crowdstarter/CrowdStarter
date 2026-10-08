from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Campaign(models.Model):
    class Status(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        ACTIVA = "ACTIVA", "Activa"
        FINANCIADA = "FINANCIADA", "Financiada"
        NO_FINANCIADA = "NO_FINANCIADA", "No financiada"

    title = models.CharField(max_length=120)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    image = models.ImageField(upload_to="campaigns/", blank=True)
    funding_goal = models.DecimalField(max_digits=12, decimal_places=2)
    deadline = models.DateField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(max_length=13, choices=Status.choices, default=Status.BORRADOR)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        constraints = [models.CheckConstraint(condition=models.Q(funding_goal__gt=0), name="positive_goal")]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("campaign_detail", args=[self.pk])

    @property
    def raised_amount(self):
        return self.contributions.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    @property
    def progress(self):
        return self.raised_amount * 100 / self.funding_goal if self.funding_goal else Decimal("0")

    @property
    def image_url(self):
        if self.image:
            from PIL import Image
            try:
                with self.image.storage.open(self.image.name, "rb") as source:
                    with Image.open(source) as picture:
                        if picture.format not in {"JPEG", "PNG"}:
                            return static("campaigns/default.svg")
                        picture.verify()
                return self.image.url
            except (OSError, ValueError):
                pass
        return static("campaigns/default.svg")

    @classmethod
    def expire_overdue(cls):
        cls.objects.filter(status=cls.Status.ACTIVA, deadline__lt=timezone.localdate()).update(
            status=cls.Status.NO_FINANCIADA, updated_at=timezone.now())


class Contribution(models.Model):
    campaign = models.ForeignKey(Campaign, related_name="contributions", on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(amount__gt=0), name="positive_contribution")]
