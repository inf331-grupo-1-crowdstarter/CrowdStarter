from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from .forms import LoginForm, RegisterForm

def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Cuenta creada correctamente. Ya puedes iniciar sesión."
            )
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = LoginForm(request=request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())

        next_url = request.POST.get("next") or request.GET.get("next")

        if next_url:
            return redirect(next_url)

        return redirect("home")

    return render(
        request,
        "registration/login.html",
        {
            "form": form,
            "next": request.GET.get("next", ""),
        },
    )

def user_logout(request):
    logout(request)
    return redirect("home")

@login_required
def protected_view(request):
    return render(request, "protected.html")

def home(request):
    return campaign_list(request)

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from .models import Campaign, Category


def campaign_list(request):
    Campaign.expire_overdue()
    campaigns = Campaign.objects.exclude(status=Campaign.Status.BORRADOR).select_related("category")
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    status = request.GET.get("status", "")
    if query:
        # SQLite LIKE does not fold accented uppercase letters.
        matching_ids = [pk for pk, title, description in campaigns.values_list("pk", "title", "description")
                        if query.casefold() in title.casefold() or query.casefold() in description.casefold()]
        campaigns = campaigns.filter(pk__in=matching_ids)
    if category:
        campaigns = campaigns.filter(category_id=category) if category.isdecimal() and len(category) < 10 else campaigns.none()
    if status:
        campaigns = campaigns.filter(status=status)
    filters = request.GET.copy()
    filters.pop("page", None)
    page = Paginator(campaigns, 10).get_page(request.GET.get("page"))
    return render(request, "campaigns/list.html", {"page_obj": page, "query": query, "selected_category": category,
        "selected_status": status, "categories": Category.objects.all(),
        "statuses": Campaign.Status.choices[1:], "filter_query": filters.urlencode()})


def campaign_detail(request, pk):
    Campaign.expire_overdue()
    campaign = get_object_or_404(Campaign, pk=pk)
    if campaign.status == Campaign.Status.BORRADOR and campaign.creator_id != request.user.pk:
        from django.http import Http404
        raise Http404
    return render(request, "campaigns/detail.html", {"campaign": campaign})


from .forms import CampaignForm
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.utils import timezone


@login_required
def campaign_create(request):
    form = CampaignForm(request.POST if request.method == "POST" else None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        campaign = form.save(commit=False)
        campaign.creator = request.user
        campaign.save()
        messages.success(request, "Campaña creada correctamente como borrador.")
        return redirect(campaign)
    return render(request, "campaigns/form.html", {"form": form, "heading": "Crear campaña"})


@login_required
@require_POST
def campaign_publish(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, creator=request.user)
    if campaign.status != Campaign.Status.BORRADOR or campaign.deadline <= timezone.localdate():
        return HttpResponseForbidden("Solo se puede publicar un borrador con fecha futura.")
    campaign.status = Campaign.Status.ACTIVA
    campaign.save(update_fields=["status", "updated_at"])
    messages.success(request, "Campaña publicada.")
    return redirect(campaign)


from django.db import transaction


@login_required
def campaign_edit(request, pk):
    Campaign.expire_overdue()
    with transaction.atomic():
        campaign = get_object_or_404(Campaign.objects.select_for_update(), pk=pk, creator=request.user)
        if campaign.status in {Campaign.Status.FINANCIADA, Campaign.Status.NO_FINANCIADA}:
            return HttpResponseForbidden("Esta campaña ya está cerrada y no puede editarse.")
        form = CampaignForm(request.POST if request.method == "POST" else None,
                            request.FILES or None, instance=campaign)
        if request.method == "POST" and form.is_valid():
            campaign = form.save(commit=False)
            if campaign.status == Campaign.Status.ACTIVA and campaign.raised_amount >= campaign.funding_goal:
                campaign.status = Campaign.Status.FINANCIADA
            campaign.save()
            messages.success(request, "Campaña actualizada correctamente.")
            return redirect(campaign)
    return render(request, "campaigns/form.html", {"form": form, "campaign": campaign, "heading": "Editar campaña"})
