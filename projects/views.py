from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from team_finder.services import paginate_queryset

from .forms import ProjectForm
from .models import Project
from .services import get_projects_queryset


def index(request):
    return redirect("projects:list")


def project_list(request):
    projects = get_projects_queryset()
    page_obj = paginate_queryset(request, projects)

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj,
            "page_obj": page_obj,
        },
    )


def project_detail(request, project_id):
    project = get_object_or_404(get_projects_queryset(), pk=project_id)

    return render(
        request,
        "projects/project-details.html",
        {
            "project": project,
        },
    )


@login_required
def favorite_projects(request):
    projects = get_projects_queryset(request.user.favorites)
    page_obj = paginate_queryset(request, projects)

    return render(
        request,
        "projects/favorite_projects.html",
        {
            "projects": page_obj,
            "page_obj": page_obj,
        },
    )


@login_required
@require_POST
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    favorited = request.user.favorites.filter(pk=project.pk).exists()

    if favorited:
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)

    return JsonResponse(
        {
            "status": "ok",
            "favorited": not favorited,
        }
    )


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    participated = project.participants.filter(pk=request.user.pk).exists()

    if participated:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse(
        {
            "status": "ok",
            "participated": not participated,
        }
    )


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])

    return JsonResponse(
        {
            "status": "ok",
            "project_status": Project.STATUS_CLOSED,
        }
    )


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)

    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)

        return redirect("projects:detail", project_id=project.pk)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": False,
        },
    )


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.owner != request.user and not request.user.is_staff:
        return redirect("projects:detail", project_id=project.pk)

    form = ProjectForm(request.POST or None, instance=project)

    if form.is_valid():
        project = form.save()
        return redirect("projects:detail", project_id=project.pk)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": True,
        },
    )
