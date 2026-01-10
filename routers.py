from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from test_app.views import CategoryViewSet, TaskViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet)

router.register('tasks', TaskViewSet)


urlpatterns = [
    path('jwt-auth/', TokenObtainPairView.as_view()),
    path('jwt-refresh/', TokenRefreshView.as_view()),
    path('subtasks/', include('test_app.urls.subtasks')),
    # path('tasks/', include('test_app.urls.tasks')),
] + router.urls