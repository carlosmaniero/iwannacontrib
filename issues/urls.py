from django.urls import path
from . import views

app_name = 'issues'

urlpatterns = [
    path('create', views.create_issue, name='create'),
]
