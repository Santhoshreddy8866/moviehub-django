from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(
                request,
                "Passwords do not match"
            )
            return redirect("register")

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists"
            )

            return redirect("register")

        if User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "Email already exists"
            )

            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(
            request,
            "Account created successfully. Please login."
        )

        return redirect("login")

    return render(
        request,
        "accounts/register.html"
    )


def login_view(request):

    next_url = request.GET.get("next", "")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        next_url = request.POST.get(
            "next",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            # Prevent redirect("None")
            if (
                next_url
                and next_url != "None"
                and next_url != "null"
            ):
                return redirect(next_url)

            return redirect("home")

        messages.error(
            request,
            "Invalid username or password"
        )

    return render(
        request,
        "accounts/login.html",
        {
            "next": next_url or ""
        }
    )


def logout_view(request):

    logout(request)

    return redirect("home")