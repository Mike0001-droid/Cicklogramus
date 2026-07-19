from .views import ProjectViewSet, TaskViewSet, WorkerViewSet, OperationBlockViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'workers', WorkerViewSet)
router.register(r'operation-blocks', OperationBlockViewSet)


