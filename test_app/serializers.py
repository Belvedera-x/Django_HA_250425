from django.utils import timezone
from test_app.models import SubTask, Task, Category
from rest_framework import serializers
from typing import Any
from django.contrib.auth.password_validation import validate_password
from test_app.models import User
import re


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Task
        fields = '__all__'



class SubTaskCreateSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
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
            'status',
            'owner',
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

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True
    )
    re_password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'gender',
            'password',
            're_password',
        ]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        first_name = attrs.get('first_name')
        last_name = attrs.get('last_name')
        password = attrs.get('password')
        re_password = attrs.pop('re_password', None)

        re_pattern = r"^[a-zA-Z]+$"

        if not first_name:
            raise serializers.ValidationError(
                {"first_name": "Это поле обязательно к заполнению"}
            )

        if not last_name:
            raise serializers.ValidationError(
                {"last_name": "Это поле обязательно к заполнению"}
            )

        if not re.match(re_pattern, first_name):
            raise serializers.ValidationError(
                {
                    "first_name": "Должно состоять только из латиницы"
                }
            )

        if not re.match(re_pattern, last_name):
            raise serializers.ValidationError(
                {
                    "last_name": "Должно состоять только из латиницы"
                }
            )

        if not password:
            raise serializers.ValidationError(
                {
                    "password": "Это поле обязательно к заполнению"
                }
            )

        if not re_password:
            raise serializers.ValidationError(
                {
                    "re_password": "Это поле обязательно к заполнению"
                }
            )

        validate_password(password)

        if password != re_password:
            raise serializers.ValidationError(
                {
                    "re_password": "Пароли должны совпадать"
                }
            )

        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)

        user.save()

        return user
