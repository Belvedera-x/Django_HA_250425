from django.urls import path
from test_app.views import SubTaskListCreateView, SubTaskDetailUpdateDeleteView

urlpatterns = [
    path('',SubTaskListCreateView.as_view()),
    path('<int:pk>/', SubTaskDetailUpdateDeleteView.as_view()),
]