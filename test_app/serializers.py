from django.utils import timezone
from test_app.models import SubTask, Task, Category
from rest_framework import serializers



class SubTaskCreateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SubTask
        fields = [
            'id',
            'title',
            'description',
            'created_at',
            'deadline',
            'task',
            'status'
        ]


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name'
        ]


    def create(self, validated_data):
        name = validated_data.get('name')
        if Category.objects.filter(name=name).exists():
            raise serializers.ValidationError({"name": "Category c таким name уже существует"})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        name = validated_data.get('name')
        if Category.objects.filter(name=name).exclude(id=instance.id).exists():
            raise serializers.ValidationError({"name": "Category c таким name уже существует"})
        return super().update(instance, validated_data)



class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = [
            'id',
            'title',
            'status',
            'deadline'
        ]

class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'deadline',
            'created_at',
            'categories',
            'subtasks'
        ]



class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'categories',
            'status',
            'deadline',
            'created_at'
        ]
        extra_kwargs = {
            'created_at': {
                'read_only': True
            }
        }


    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Дата дедлайна не может быть в прошлом")
        return value