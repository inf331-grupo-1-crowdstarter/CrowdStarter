from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import RegisterForm


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


def home(request):
    return render(request, "home.html")