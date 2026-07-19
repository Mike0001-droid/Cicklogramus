from django.contrib import admin
from .models import Worker, Project, Task, OperationBlock, OperationBlockItem


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1
    fields = ('name', 'duration',)
    

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'task_count', 'created_at')
    search_fields = ('name', 'description')
    inlines = [TaskInline]
    
    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = 'Кол-во задач'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project',)
    search_fields = ('name', 'project__name')


class WorkerAdmin(admin.ModelAdmin):
    list_display = ['name', ]

admin.site.register(Worker, WorkerAdmin)
admin.site.register(OperationBlock)
admin.site.register(OperationBlockItem)
