from django.contrib import admin
from django.urls import path, include

from triage.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('issues/', include('issues.urls', namespace='issues')),
    path('', home, name='home')
]
