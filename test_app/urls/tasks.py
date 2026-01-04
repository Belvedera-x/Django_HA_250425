from django.urls import path
from test_app.views import (
    TaskListCreateGenericView,
    TaskRetrieveUpdateDestroyGenericView,
    TaskStatsView,
)

urlpatterns = [
    path("", TaskListCreateGenericView.as_view()),
    path("<int:pk>/", TaskRetrieveUpdateDestroyGenericView.as_view()),
    path("stats/", TaskStatsView.as_view()),
]