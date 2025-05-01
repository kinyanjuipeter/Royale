"""
URL configuration for electronics_shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from shop.admin import admin_site
from django.views.generic import RedirectView
from django.http import HttpResponse

# Customize admin site
admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.index_title = settings.ADMIN_INDEX_TITLE

def healthcheck(request):
    return HttpResponse("OK")

urlpatterns = [
    # Root URL returns 200 OK for Railway health check
    path('', healthcheck, name='healthcheck'),
    
    # Admin URLs
    path('admin/', admin_site.urls),
    
    # Shop URLs
    path('shop/', include('shop.urls', namespace='shop')),
    
    # Registration URLs
    path('accounts/', include('registration.urls', namespace='registration')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                        document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
