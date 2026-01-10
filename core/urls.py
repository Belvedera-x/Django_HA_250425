"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from test_app.views import home_page
from test_app.views import name_page
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title='Test Swagger',
        default_version='1.0.0',
        description='TEST DESCRIPTION',
        # terms_of_service='https://policies.google.com/terms?hl=en-US',
        # contact=openapi.Contact(name='Sergii', email='test.gmail@gmail.com'),
        # license=openapi.License(name='AWESOME LICENSE')
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_page),
    path('<str:user_name>', name_page),
    path('api/v1/', include('routers')),

    # SWAGGER
    path(
        'swagger/',
        schema_view.with_ui('swagger')
    ),
    path(
        'redoc/',
        schema_view.with_ui('redoc')
    )
]
