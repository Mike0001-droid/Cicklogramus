from django.core.management.base import BaseCommand
from cicklogramus.models import Task, Project


class Command(BaseCommand):
    help = 'Fill position field for existing tasks based on start_time ordering'

    def handle(self, *args, **options):
        for project in Project.objects.all():
            tasks = Task.objects.filter(project=project).order_by('start_time')
            for index, task in enumerate(tasks):
                task.position = index
                task.save()
                self.stdout.write(f'Updated task {task.name} position to {index}')

        self.stdout.write(self.style.SUCCESS('Successfully filled position field for all tasks'))
