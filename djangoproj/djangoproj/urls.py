"""djangoproj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from mainsite import views

router = routers.DefaultRouter()
#router.register(r'showshort', views.ShowShortViewSet)

urlpatterns = [
    path('', include ('mainsite.urls')),
    path('', include ('mylogin.urls')),
    path('api/', include(router.urls)),
    path('api/showshort/', views.ShowShortViewSet.as_view(), name = 'showshort'),
    path('api-auth/', include('rest_framework.urls', namespace = 'rest_framework')),
    path('su/per/se/cret/', admin.site.urls),
]
