from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
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
from .models import Campaign


def campaign_list(request):
    Campaign.expire_overdue()
    campaigns = Campaign.objects.exclude(status=Campaign.Status.BORRADOR).select_related("category")
    page = Paginator(campaigns, 10).get_page(request.GET.get("page"))
    return render(request, "campaigns/list.html", {"page_obj": page})


def campaign_detail(request, pk):
    Campaign.expire_overdue()
    campaign = get_object_or_404(Campaign, pk=pk)
    if campaign.status == Campaign.Status.BORRADOR and campaign.creator_id != request.user.pk:
        from django.http import Http404
        raise Http404
    return render(request, "campaigns/detail.html", {"campaign": campaign})
