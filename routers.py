from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter


router = SimpleRouter()


urlpatterns = [
    path('subtasks/', include('test_app.urls.subtasks')),
    path('tasks/', include('test_app.urls.tasks')),
] + router.urls