from django.shortcuts import render

from triage.forms import SearchForm


def home(request):
    form = SearchForm()

    if request.GET.get('language'):
        form = SearchForm(request.GET)

    return render(request, 'triage/home.html', {
        "form": form,
    })
