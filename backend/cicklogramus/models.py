from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Task(models.Model):    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=200)
    worker = models.ForeignKey('Worker', verbose_name="Исполнитель", on_delete=models.CASCADE, related_name='tasks')
    color = models.CharField("Цвет операции в таблице", max_length=30, null=False, default='#3498db')
    duration = models.IntegerField("Длительность операции (в секундах)", default=10)
    start_time = models.IntegerField("Секунда старта", null=True, blank=True)
    finish_time = models.IntegerField("Секунда финиша", null=True, blank=True)
    position = models.IntegerField("Позиция в списке", default=0)
    dependencies = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependent_tasks')

    class Meta:
        ordering = ['position']

    def update_dependent_tasks(self, visited=None):
        if visited is None:
            visited = set()
        visited.add(self.id)

        dependents = Task.objects.filter(dependencies=self)
        for dependent in dependents:
            if dependent.id in visited:
                continue

            max_finish_time = dependent.dependencies.aggregate(
                models.Max('finish_time')
            )['finish_time__max']
            new_start_time = max_finish_time or 0

            if dependent.start_time != new_start_time:
                dependent.start_time = new_start_time
                dependent.finish_time = new_start_time + dependent.duration
                dependent.save(update_dependents=False)
                dependent.update_dependent_tasks(visited)

    def save(self, *args, **kwargs):
        update_dependents = kwargs.pop('update_dependents', True)
        is_new = self.pk is None
        old_finish_time = None

        if not is_new:
            try:
                old_task = Task.objects.get(pk=self.pk)
                old_duration = old_task.duration
                old_start_time = old_task.start_time
                old_finish_time = old_task.finish_time

                first_task = Task.objects.filter(project=self.project).order_by('id').first()
                if first_task and first_task.id == self.id:
                    self.start_time = 0
                    self.finish_time = self.duration
                    super().save(*args, **kwargs)
                    return

                if self.duration != old_duration:
                    if self.finish_time is None:
                        self.finish_time = (self.start_time or 0) + self.duration
                    else:
                        self.finish_time += self.duration - old_duration

                if self.start_time != old_start_time:
                    self.finish_time = (self.start_time or 0) + self.duration

            except Task.DoesNotExist:
                pass

        else:
            if self.position is None:
                last_position = Task.objects.filter(project=self.project).aggregate(
                    models.Max('position')
                )['position__max']
                if last_position is not None:
                    self.position = last_position + 1

            first_task = Task.objects.filter(project=self.project).order_by('id').first()
            if not first_task or first_task.id == self.id:
                self.start_time = 0
                self.finish_time = self.duration
            else:
                last_task = Task.objects.filter(project=self.project).order_by('-finish_time').first()
                if last_task and last_task.id != self.id:
                    self.start_time = last_task.finish_time
                    self.finish_time = last_task.finish_time + self.duration
                else:
                    self.start_time = 0
                    self.finish_time = self.duration        

        super().save(*args, **kwargs)

        if update_dependents and not is_new and old_finish_time != self.finish_time:
            self.update_dependent_tasks()
    
    def __str__(self):
        return f"{self.name} ({self.project.name})"
    

class OperationBlock(models.Model):
    name = models.CharField(max_length=200)
    worker = models.ForeignKey('Worker', on_delete=models.CASCADE, related_name='operation_blocks')
    source_project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operation_blocks'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class OperationBlockItem(models.Model):
    block = models.ForeignKey(OperationBlock, on_delete=models.CASCADE, related_name='items')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='operation_block_items')
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position', 'id']
        constraints = [
            models.UniqueConstraint(fields=['block', 'position'], name='unique_block_position')
        ]


class Worker(models.Model):
    name = models.CharField("Название исполнителя", max_length=150, null=False)
    color = models.CharField("Цвет исполнителя в таблице", max_length=30, null=False)

    def __str__(self):
        return self.name
