from django.urls import path
from test_app.views import (
    SubTaskListCreateGenericView,
    SubTaskRetrieveUpdateDestroyGenericView,
)

urlpatterns = [
    path("", SubTaskListCreateGenericView.as_view()),
    path("<int:pk>/", SubTaskRetrieveUpdateDestroyGenericView.as_view()),
]