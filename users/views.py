from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from team_finder.constants import USERS_PER_PAGE
from team_finder.services import paginate_queryset

from .forms import (EditProfileForm, LoginForm, PasswordChangeUserForm,
                    RegisterForm)
from .models import User
from .services import get_ordered_users


def register_view(request):
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        User.objects.create_user(
            email=form.cleaned_data["email"],
            name=form.cleaned_data["name"],
            surname=form.cleaned_data["surname"],
            password=form.cleaned_data["password"],
        )

        return redirect("users:login")

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request.POST or None)

    if form.is_valid():
        login(request, form.cleaned_data["user"])
        return redirect("projects:list")

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_detail(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)

    return render(
        request,
        "users/user-details.html",
        {
            "user": profile_user,
        },
    )


@login_required
def edit_profile(request):
    form = EditProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )

    if form.is_valid():
        form.save()
        return redirect("users:detail", user_id=request.user.pk)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = PasswordChangeUserForm(user=request.user, data=request.POST or None)

    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:detail", user_id=request.user.pk)

    return render(request, "users/change_password.html", {"form": form})


def users_list(request):
    participants = get_ordered_users()
    active_filter = request.GET.get("filter")

    if request.user.is_authenticated and active_filter:
        current_user = request.user

        if active_filter == "favorite_authors":
            participants = User.objects.filter(
                owned_projects__interested_users=current_user
            ).distinct()

        elif active_filter == "participated_project_authors":
            participants = User.objects.filter(
                owned_projects__participants=current_user
            ).distinct()

        elif active_filter == "my_projects_liked_by":
            participants = User.objects.filter(
                favorites__owner=current_user
            ).distinct()

        elif active_filter == "my_project_participants":
            participants = User.objects.filter(
                participated_projects__owner=current_user
            ).distinct()

    page_obj = paginate_queryset(request, participants, USERS_PER_PAGE)

    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj,
            "page_obj": page_obj,
            "active_filter": active_filter,
            "active_skill": active_filter,
        },
    )
