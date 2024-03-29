"""import URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf import settings
from django.urls import include, re_path
from rest_framework_swagger.views import get_swagger_view

urlpatterns = [
    re_path(r"", include("api.urls")),
    re_path(r"^status/", include("health.urls")),
]


if settings.DEBUG:
    import debug_toolbar

    schema_view = get_swagger_view(title="WBA Kaart API")

    urlpatterns.extend(
        [re_path(r"^__debug__/", include(debug_toolbar.urls)), re_path(r"^docs/$", schema_view)]
    )
