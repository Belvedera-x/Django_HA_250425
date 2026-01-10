from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse, HttpRequest
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from test_app.utils import set_jwt_cookies
from django.contrib.auth import authenticate
from permissions import IsModeratorOrAdmin, IsAdmin, IsOwnerOrReadOnly
from test_app.models import SubTask, Task, Category
from test_app.paginator import MyPagPaginator
from test_app.serializers import (
    SubTaskSerializer,
    TaskDetailSerializer,
    SubTaskCreateSerializer,
    TaskSerializer,
    CategoryCreateSerializer,
    UserCreateSerializer
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
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = []

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my(self, request):
        tasks = Task.objects.filter(owner=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)



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
    permission_classes = [AllowAny]
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
    permission_classes = [IsModeratorOrAdmin]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]

    filterset_fields = ["status", "deadline"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



class TaskRetrieveUpdateDestroyGenericView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class TaskStatsView(APIView):
    permission_classes = [IsModeratorOrAdmin]
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
    permission_classes = [IsModeratorOrAdmin]
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

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SubTaskRetrieveUpdateDestroyGenericView(
    generics.RetrieveUpdateDestroyAPIView
):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
    ordering = ["id"]
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return []
        return [IsAdmin()]

    def perform_destroy(self, instance):
        instance.delete()  # soft delete

    @action(detail=True, methods=['get'])
    def count_tasks(self, request, pk=None):
        category = self.get_object()
        return Response({
            "category_id": category.id,
            "tasks_count": category.tasks.count()
        })


class RegisterUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = UserCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()

        response = Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

        set_jwt_cookies(response, user)

        return response



class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"message": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            request=request,
            username=username,
            password=password
        )

        if not user:
            return Response(
                {"message": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        response = Response(status=status.HTTP_200_OK)
        set_jwt_cookies(response, user)
        return response


class LogOutUser(APIView):
    def post(self, request: Request) -> Response:
        try:
            refresh = request.COOKIES.get('refresh_token')

            if refresh:
                token = RefreshToken(refresh)
                token.blacklist()

        except Exception as exc:
            return Response(
                data={
                    "message": str(exc)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        response = Response(status=status.HTTP_200_OK)

        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response
