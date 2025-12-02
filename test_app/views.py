from django.http import HttpResponse, HttpRequest
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils import timezone
from test_app.models import SubTask, Task, TaskStatus
from test_app.serializers import SubTaskSerializer, TaskCreateSerializer, TaskDetailSerializer


def home_page(request: HttpRequest):
    return HttpResponse(
        f"<h1>Hello from our first endpoint!!!</h1>"
    )

def name_page(request: HttpRequest, user_name):
    return HttpResponse(
        f"<h1>Hello {user_name}!!!</h1>"
    )


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
            "new": tasks.filter(status="new").count(),
            "in_progress": tasks.filter(status="in_progress").count(),
            "pending": tasks.filter(status="pending").count(),
            "blocked": tasks.filter(status="blocked").count(),
            "done": tasks.filter(status="done").count(),
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
        serializer = SubTaskSerializer(subtasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubTaskSerializer(data=request.data)
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
