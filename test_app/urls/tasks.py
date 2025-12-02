from django.urls import path
from test_app.views import TaskListCreateView, TaskStatsView

urlpatterns = [
    path('',TaskListCreateView.as_view()),
    path('<int:pk>/', TaskListCreateView.as_view()),
    path('stats/', TaskStatsView.as_view()),

]