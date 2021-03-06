"""death_star URL Configuration

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
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls import url
import death_star.views
from django.contrib.auth.decorators import login_required


schema_view = get_schema_view(
   openapi.Info(
      title="DOKA endpoints",
      default_version='v1',
      description="Egor\'s development server",
      # terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="egor.wexler@surecomp.com"),
      # license=openapi.License(name="BSD License"),
   ),
   public=True,
   # permission_classes=(permissions.AllowAny,),
)

@login_required(login_url='/accounts/login/')
def swa(request):
    func = schema_view.with_ui('swagger', cache_timeout=0)
    return func(request)


urlpatterns = [
    path("admin/", admin.site.urls),
    # path("exhaust_port/", include("exhaust_port.urls")),
    # path("doka/test_autogen/", include("test_autogen.urls")),
    path("doka/excel/", include("excelfee.urls")),
    path('accounts/', include('django.contrib.auth.urls')),
    # path("accounts/login/", death_star.views.login),
    # path("accounts/logout/", death_star.views.logout),
    path("", death_star.views.login),

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^swagger/$', swa, name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
