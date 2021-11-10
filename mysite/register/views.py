from django.shortcuts import render, redirect
from .forms import RegisterForm
from main import database as db


# Create your views here.
def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            try:
                form.save()
                db.make_customer(
                    form.cleaned_data["username"],
                    form.cleaned_data["password1"],
                    form.cleaned_data["first"],
                    form.cleaned_data["last"],
                    form.cleaned_data["phone"],
                )
                return redirect("/")
            except:
                return render(response, "register/register.html", {"form": form})
    else:
        form = RegisterForm()
    return render(response, "register/register.html", {"form": form})
