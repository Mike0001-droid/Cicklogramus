from rest_framework import viewsets, status
from .utils import export_gantt_chart, export_cyclogram_exact
from .exceptions import NoTaskException
from .models import Project, Task, Worker, OperationBlock
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import (ProjectSerializer, ProjectListSerializer,
                          TaskSerializer, TaskListSerializer,
                          WorkerSerializer, OperationBlockSerializer)
from django.shortcuts import get_object_or_404


class WorkerViewSet(viewsets.ModelViewSet):
    serializer_class = WorkerSerializer
    queryset = Worker.objects.all()


class OperationBlockViewSet(viewsets.ModelViewSet):
    serializer_class = OperationBlockSerializer
    queryset = OperationBlock.objects.prefetch_related('items__task').select_related(
        'worker',
        'source_project'
    )


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def get_queryset(self):
        # Оптимизированный queryset с select_related для создателя
        return Project.objects.select_related('created_by').all()

    def get_serializer_class(self):
        """Используем разные сериализаторы для списка и детального просмотра"""
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Получить только задачи конкретного проекта (без полной перезагрузки)"""
        project = self.get_object()
        tasks = project.tasks.select_related('worker').all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def export_cyclogram(self, request, pk=None):
        try:
            return export_cyclogram_exact(pk)
        except NoTaskException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get_queryset(self):
        # Оптимизированный queryset с select_related для worker и project
        return Task.objects.select_related('project', 'worker').all()

    def get_serializer_class(self):
        """Используем упрощённый сериализатор для списка"""
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        dependencies = request.data['dependencies']

        if dependencies != instance.dependencies:
            if not dependencies:
                pass
            else:
                parent_task = get_object_or_404(Task, pk = dependencies[0])
                request.data['start_time'] = parent_task.finish_time

        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        tasks_data = request.data.get('tasks', [])
        for task_data in tasks_data:
            try:
                task = Task.objects.get(id=task_data['id'])
                serializer = TaskSerializer(task, data=task_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
            except Task.DoesNotExist:
                continue

        project_id = request.data.get('project_id')
        tasks = Task.objects.filter(project_id=project_id)
        return Response(TaskSerializer(tasks, many=True).data)

    @action(detail=False, methods=['post'])
    def reorder_tasks(self, request):
        """Переупорядочивание задач с сохранением позиций"""
        task_ids = request.data.get('task_ids', [])
        project_id = request.data.get('project_id')

        if not task_ids or not project_id:
            return Response({'error': 'task_ids and project_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Обновляем позиции задач
        for index, task_id in enumerate(task_ids):
            try:
                task = Task.objects.get(id=task_id, project_id=project_id)
                task.position = index
                task.save()
            except Task.DoesNotExist:
                continue

        tasks = Task.objects.filter(project_id=project_id)
        return Response(TaskSerializer(tasks, many=True).data)
    
    @action(detail=True, methods=['get'])
    def export_gantt_chart(self, request, pk):
        try:
            return export_gantt_chart(pk)
        except NoTaskException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
