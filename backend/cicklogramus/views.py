from rest_framework import viewsets, status
from .utils import export_gantt_chart, export_cyclogram_exact
from .exceptions import NoTaskException
from .models import Project, Task, Worker, OperationBlock
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from .serializers import (ProjectSerializer, ProjectListSerializer,
                          TaskSerializer, TaskListSerializer,
                          WorkerSerializer, OperationBlockSerializer)
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import logout
from rest_framework.permissions import AllowAny, IsAuthenticated


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

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Массовое удаление задач"""
        task_ids = request.data.get('task_ids', [])

        if not task_ids:
            return Response({'error': 'task_ids are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Удаляем задачи
        deleted_count = 0
        for task_id in task_ids:
            try:
                task = Task.objects.get(id=task_id)
                task.delete()
                deleted_count += 1
            except Task.DoesNotExist:
                continue

        return Response({
            'message': f'Удалено {deleted_count} задач',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)
    @action(detail=True, methods=['get'])
    def export_gantt_chart(self, request, pk):
        try:
            return export_gantt_chart(pk)
        except NoTaskException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Регистрация нового пользователя"""
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')

    # Валидация
    if not username or not password:
        return Response(
            {'error': 'Имя пользователя и пароль обязательны'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(password) < 6:
        return Response(
            {'error': 'Пароль должен содержать минимум 6 символов'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Проверка существования пользователя
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Пользователь с таким именем уже существует'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Создание пользователя
    try:
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        return Response({
            'message': 'Пользователь успешно создан',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {'error': f'Ошибка при создании пользователя: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    """Получение статистики текущего пользователя"""
    user = request.user

    # Считаем количество проектов и задач пользователя
    projects_count = Project.objects.filter(created_by=user).count()
    tasks_count = Task.objects.filter(project__created_by=user).count()

    return Response({
        'projects': projects_count,
        'tasks': tasks_count
    })


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Получение и обновление профиля текущего пользователя"""
    user = request.user

    if request.method == 'GET':
        return Response({
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined
        })

    elif request.method == 'PUT':
        email = request.data.get('email', '')
        password = request.data.get('password')

        # Обновляем email если указан
        if email:
            user.email = email

        # Обновляем пароль если указан
        if password:
            if len(password) < 6:
                return Response(
                    {'password': ['Пароль должен содержать минимум 6 символов']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(password)

        user.save()

        return Response({
            'username': user.username,
            'email': user.email,
            'message': 'Профиль успешно обновлен'
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    """Выход из системы - завершает Django сессию"""
    # Завершаем Django сессию (удаляем сессионные куки)
    logout(request)

    return Response({
        'message': 'Вы успешно вышли из системы'
    }, status=status.HTTP_200_OK)
