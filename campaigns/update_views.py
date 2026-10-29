from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .models import Campaign, CampaignUpdate
from .update_forms import CampaignUpdateForm


@login_required
@require_http_methods(["GET", "POST"])
def update_create(request, pk):
    Campaign.expire_overdue()
    with transaction.atomic():
        # Serialize status checks with campaign writes, including on SQLite.
        if request.method == "POST":
            Campaign.objects.filter(pk=pk, creator=request.user).update(updated_at=F("updated_at"))
        campaign = get_object_or_404(Campaign.objects.select_for_update(), pk=pk, creator=request.user)
        if not campaign.can_publish_updates:
            return HttpResponseForbidden("Solo se pueden publicar actualizaciones en campañas activas o financiadas.")
        form = CampaignUpdateForm(request.POST if request.method == "POST" else None)
        if request.method == "POST" and form.is_valid():
            update = form.save(commit=False)
            update.campaign = campaign
            update.author = request.user
            update.save()
            messages.success(request, "Actualización publicada correctamente.")
            return redirect(campaign.get_absolute_url() + "#actualizaciones")
    return render(request, "campaigns/update_form.html", {
        "campaign": campaign, "form": form, "heading": "Publicar actualización"})


@login_required
@require_http_methods(["GET", "POST"])
def update_edit(request, pk, update_pk):
    campaign = get_object_or_404(Campaign, pk=pk, creator=request.user)
    update = get_object_or_404(CampaignUpdate, pk=update_pk, campaign=campaign, author=request.user)
    form = CampaignUpdateForm(request.POST if request.method == "POST" else None, instance=update)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Actualización editada correctamente.")
        return redirect(campaign.get_absolute_url() + "#actualizaciones")
    return render(request, "campaigns/update_form.html", {
        "campaign": campaign, "form": form, "heading": "Editar actualización"})


@login_required
@require_POST
def update_delete(request, pk, update_pk):
    campaign = get_object_or_404(Campaign, pk=pk, creator=request.user)
    update = get_object_or_404(CampaignUpdate, pk=update_pk, campaign=campaign, author=request.user)
    update.delete()
    messages.success(request, "Actualización eliminada correctamente.")
    return redirect(campaign.get_absolute_url() + "#actualizaciones")
