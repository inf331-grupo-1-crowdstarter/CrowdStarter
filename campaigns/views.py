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
    return render(request, "home.html")