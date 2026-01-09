from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter

from test_app.views import CategoryViewSet


router = DefaultRouter()
router.register('categories', CategoryViewSet)


urlpatterns = [
    path('subtasks/', include('test_app.urls.subtasks')),
    path('tasks/', include('test_app.urls.tasks')),
] + router.urls