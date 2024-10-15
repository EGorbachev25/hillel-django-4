"""
URL configuration for hillelDjango4 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from allauth.account.views import LogoutView
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from graphene_django.views import GraphQLView
from rest_framework import permissions
from rest_framework.authtoken import views as authtoken_views
from rest_framework.routers import DefaultRouter

from orders.viewsets import OrderViewSet
from products.viewsets import ProductViewSet
from telegram.views import telegram
from .views import hello_world, index, current_time

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('orders', OrderViewSet)

schema_view = get_schema_view(
   openapi.Info(
      title="Store API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="vitalii@vitalii.tech"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-token-auth/', authtoken_views.obtain_auth_token),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('hello-world', hello_world),
    path('telegram', telegram),
    path("accounts/", include("allauth.urls")),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("graphql", GraphQLView.as_view(graphiql=True)),
    path("time", current_time, name="time"),
    path("", index, name="index"),
]
