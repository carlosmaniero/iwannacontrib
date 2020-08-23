from django.shortcuts import render

from issues.forms import CreateIssueForm


def create_issue(request):
    form = CreateIssueForm()

    if request.method == 'POST':
        form = CreateIssueForm(request.POST)

    return render(request, 'issues/create_issue.html', {
        "form": form
    })
