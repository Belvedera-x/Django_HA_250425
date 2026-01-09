from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend

from django.http import HttpResponse, HttpRequest
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.viewsets import ModelViewSet

from test_app.models import SubTask, Task, Category
from test_app.paginator import MyPagPaginator
from test_app.serializers import (
    SubTaskSerializer,
    TaskCreateSerializer,
    TaskDetailSerializer,
    SubTaskCreateSerializer,
    TaskSerializer, CategoryCreateSerializer
)

def home_page(request: HttpRequest):
    return HttpResponse(
        f"<h1>Hello from our first endpoint!!!</h1>"
    )

def name_page(request: HttpRequest, user_name):
    return HttpResponse(
        f"<h1>Hello {user_name}!!!</h1>"
    )

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by("-created_at")
    serializer_class = TaskSerializer
    filter_backends = []



    def get_queryset(self):
        queryset = Task.objects.all().order_by("-created_at")
        day_of_week = self.request.query_params.get("day_of_week")
        if day_of_week:
            days = {
                'monday': 2,
                'tuesday': 3,
                'wednesday': 4,
                'thursday': 5,
                'friday': 6,
                'saturday': 7,
                'sunday': 1,
            }
            day_number = days.get(day_of_week.lower())
            if day_number:
                queryset = queryset.filter(deadline__week_day=day_number)
        return queryset



class SubtaskFilterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubTask.objects.all().order_by("-created_at")
    serializer_class = SubTaskSerializer
    pagination_class = MyPagPaginator

    def get_queryset(self):
        queryset = super().get_queryset()
        task_title = self.request.query_params.get("task_title")
        status_params = self.request.query_params.get("status")

        if task_title:
            queryset = queryset.filter(task__title__icontains=task_title.strip())

        if status_params:
            queryset = queryset.filter(status__iexact=status_params.strip())

        return queryset



class TaskListCreateGenericView(generics.ListCreateAPIView):
    queryset = Task.objects.all().order_by("-created_at")
    serializer_class = TaskSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    filterset_fields = ["status", "deadline"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]



class TaskRetrieveUpdateDestroyGenericView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer


class TaskStatsView(APIView):
    def get(self, request):
        tasks = Task.objects.all()
        total_tasks = tasks.count()

        status_counts = {
            "new": tasks.filter(status="NEW").count(),
            "in_progress": tasks.filter(status="IN_PROGRESS").count(),
            "pending": tasks.filter(status="PENDING").count(),
            "blocked": tasks.filter(status="BLOCKED").count(),
            "done": tasks.filter(status="DONE").count(),
        }

        overdue_tasks = tasks.filter(deadline__lt=timezone.now()).count()

        data = {
            "total_tasks": total_tasks,
            "status_counts": status_counts,
            "overdue_tasks": overdue_tasks,
        }
        return Response(data, status=status.HTTP_200_OK)


class SubTaskListCreateGenericView(generics.ListCreateAPIView):
    queryset = SubTask.objects.all().order_by("-created_at")
    serializer_class = SubTaskCreateSerializer
    pagination_class = MyPagPaginator

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    filterset_fields = ["status", "deadline"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]


class SubTaskRetrieveUpdateDestroyGenericView(
    generics.RetrieveUpdateDestroyAPIView
):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer

    def perform_destroy(self, instance):
        instance.delete()  # soft delete

    @action(detail=True, methods=['get'])
    def count_tasks(self, request, pk=None):
        category = self.get_object()
        return Response({
            "category_id": category.id,
            "tasks_count": category.tasks.count()
        })
