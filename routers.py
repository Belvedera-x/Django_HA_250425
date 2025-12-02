from django.urls import path, include

urlpatterns = [
    path('subtasks/', include('test_app.urls.subtasks')),
    path('tasks/', include('test_app.urls.tasks')),
]