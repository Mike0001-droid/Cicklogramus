from django.db import models
from rest_framework import serializers
from .models import Project, Task, Worker, OperationBlock, OperationBlockItem
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для JWT токена с дополнительными полями"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Добавляем пользовательскиеClaims
        token['username'] = user.username
        token['email'] = user.email

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Добавляем информацию о пользователе в ответ
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email
        }

        return data


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    """Полный сериализатор задачи для детального просмотра"""
    worker_name = serializers.CharField(source='worker.name', read_only=True)
    worker_label = serializers.CharField(source='worker.label', read_only=True)
    worker_color = serializers.CharField(source='worker.color', read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('id',)

    def create(self, validated_data):
        position_provided = 'position' in validated_data and validated_data['position'] is not None
        project = validated_data.get('project')

        if position_provided:
            Task.objects.filter(
                project=project,
                position__gte=validated_data['position']
            ).update(position=models.F('position') + 1)
        else:
            last_position = Task.objects.filter(project=project).aggregate(
                models.Max('position')
            )['position__max']
            validated_data['position'] = 0 if last_position is None else last_position + 1

        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """Упрощённый сериализатор для списка задач"""
    worker_name = serializers.CharField(source='worker.name', read_only=True)
    worker_color = serializers.CharField(source='worker.color', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'worker', 'worker_name', 'worker_color',
                  'duration', 'start_time', 'finish_time', 'position',
                  'color', 'dependencies']


class TaskUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('start_time', 'finish_time', 'duration')


class ProjectListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка проектов (без задач)"""
    task_count = serializers.IntegerField(source='tasks.count', read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'start_date', 'end_date',
                  'created_at', 'task_count']


class ProjectSerializer(serializers.ModelSerializer):
    """Полный сериализатор проекта с задачами"""
    tasks = TaskListSerializer(many=True, read_only=True)
    task_count = serializers.IntegerField(source='tasks.count', read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class OperationBlockItemSerializer(serializers.ModelSerializer):
    task_name = serializers.CharField(source='task.name', read_only=True)
    task_duration = serializers.IntegerField(source='task.duration', read_only=True)

    class Meta:
        model = OperationBlockItem
        fields = ('id', 'task', 'position', 'task_name', 'task_duration')
        read_only_fields = ('id',)


class OperationBlockSerializer(serializers.ModelSerializer):
    items = OperationBlockItemSerializer(many=True, required=False)

    class Meta:
        model = OperationBlock
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        block = OperationBlock.objects.create(**validated_data)
        for item in items_data:
            OperationBlockItem.objects.create(block=block, **item)
        return block

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        block = super().update(instance, validated_data)
        if items_data is not None:
            block.items.all().delete()
            for item in items_data:
                OperationBlockItem.objects.create(block=block, **item)
        return block
