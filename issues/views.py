from django.shortcuts import render, redirect
from github import Github

from issues.forms import CreateIssueForm
from issues.models import Issue
from issues.services.create_issue_service import CreateIssueService


def create_issue(request):
    form = CreateIssueForm()

    if request.method == 'POST':
        form = CreateIssueForm(request.POST)

        if form.is_valid():
            issue = CreateIssueService().create_issue(Github(), form.cleaned_data.get('url'))
            return redirect(issue.get_url())

    return render(request, 'issues/create_issue.html', {
        "form": form
    })


def show_issue(request, owner: str, repository: str, number: int):
    issue = Issue.objects.get(
        repository__owner__owner=owner,
        repository__name=repository,
        number=number
    )

    return render(request, 'issues/show_issue.html', {
        "issue": issue
    })


def rate(request, owner: str, repository: str, number: int):
    issue = Issue.objects.get(
        repository__owner__owner=owner,
        repository__name=repository,
        number=number
    )

    issue.rate(int(request.POST['rate']))
    issue.save()

    return redirect(issue.get_url())
