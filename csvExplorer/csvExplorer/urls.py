"""csvExplorer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django import views
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from .views import FileUploadView, success_view, file_delete

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file_upload'),
    path('admin/', admin.site.urls),
    path('success/', success_view, name='success_view'),
    path('file_delete/<int:pk>/', file_delete, name='file_delete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
