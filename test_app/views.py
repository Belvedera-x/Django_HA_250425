from django.http import HttpResponse, HttpRequest
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from django.utils import timezone
from test_app.models import SubTask, Task
from test_app.paginator import MyPagPaginator
from test_app.serializers import (
    SubTaskSerializer,
    TaskCreateSerializer,
    TaskDetailSerializer,
    SubTaskCreateSerializer,
    TaskSerializer
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



class TaskListCreateView(APIView):
    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskDetailSerializer(tasks, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class SubTaskListCreateView(APIView):
    def get(self, request):
        subtasks = SubTask.objects.all()
        serializer = SubTaskCreateSerializer(subtasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class SubTaskDetailUpdateDeleteView(APIView):
    def get_object(self, pk):
        try:
            return SubTask.objects.get(pk=pk)
        except SubTask.DoesNotExist:
            return None

    def get(self, request, pk):
        subtask = self.get_object(pk)
        if not subtask:
            return Response({"error": "Subtask not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubTaskSerializer(subtask)
        return Response(serializer.data)


    def put(self, request, pk):
        subtask = self.get_object(pk)
        if not subtask:
            return Response({"error": "Subtask not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubTaskSerializer(instance=subtask, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        subtask = self.get_object(pk)
        if not subtask:
            return Response({"error": "Subtask not found"}, status=status.HTTP_404_NOT_FOUND)
        subtask.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
