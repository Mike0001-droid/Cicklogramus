<template>
  <div id="app" class="project-planner">
    <div class="container-fluid h-100">
      <div class="row h-100">
        <!-- Единая Excel-сетка -->
        <div class="col-12 h-100">
          <ExcelGrid
            :projects="projects"
            :workers="workers"
            :currentProject="currentProject"
            :timelineSeconds="timelineSeconds"
            :pixelsPerSecond="pixelsPerSecond"
            @update:currentProject="handleProjectChange"
            @projectChanged="handleProjectChange"
            @addProject="addProject"
            @addTask="addTask"
            @addWorker="addWorker"
            @updateTask="updateTask"
            @updateTaskTimes="updateTaskTimes"
            @deleteTask="deleteTask"
            @addDependentTask="addDependentTask"
            @updateDependencies="updateDependencies"
            @addDependency="addDependency"
            @removeDependency="removeDependency"
            @addTaskFromTemplate="addTaskFromTemplate"
            @addTaskFromExisting="addTaskFromExisting"
            @updateWorkerColor="updateWorkerColor"
            @updateWorkerColorFromCell="updateWorkerColorFromCell"
            @exportToExcel="exportToExcel"
            @selectTask="selectTask"
            @createOperationBlock="createOperationBlock"
            @update:pixelsPerSecond="pixelsPerSecond = $event"
            :selectedTaskId="selectedTaskId"
            :selectedTaskIds="selectedTaskIds"
          />
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { projectService, workerService, taskService, operationBlockService } from '../services/api'
import { getRandomColor } from '../utils/helpers'
import ExcelGrid from './ExcelGrid.vue'
import Swal from 'sweetalert2';
export default {
  name: 'ProjectPlanner',
  components: {
    ExcelGrid
  },
  data() {
    return {
      projects: [],
      workers: [],
      currentProject: null,
      timelineSeconds: [],
      pixelsPerSecond: 20,
      maxTimelineSeconds: 60,
      loadingTaskId: null,
      taskRowHeights: {},
      taskRowHeight: 40,
      selectedTaskId: null,
      selectedTaskIds: [],
      copiedTasks: [],
      undoStack: [],
      isUndoing: false
    }
  },
  props: {
    initialProjectId: {
      type: Number,
      default: null
    }
  },
  async mounted() {
    await this.loadWorkers();
    await this.loadProjects();
    this.generateTimeline();
    this.setupKeyboardShortcuts();

    // Если указан initialProjectId, открываем этот проект
    if (this.initialProjectId) {
      const project = this.projects.find(p => p.id === this.initialProjectId);
      if (project) {
        await this.handleProjectChange(project);
      }
    }
  },
  watch: {
    currentProject: {
      handler() {
        this.generateTimeline();
      },
      deep: true
    }
  },
  methods: {
    async handleProjectChange(project) {
      console.log('🔄 Смена проекта:', project?.name);

      // Если проект уже имеет задачи, используем их
      if (project && project.tasks && project.tasks.length > 0) {
        this.currentProject = project;
      } else if (project) {
        // Иначе загружаем задачи с сервера
        await this.loadProjectTasks(project.id);
        this.currentProject = project;
      } else {
        this.currentProject = null;
      }

      this.selectedTaskId = null;
      this.selectedTaskIds = [];
      this.saveCurrentProject(project);
      this.generateTimeline();
    },

    async loadProjects() {
      try {
        this.projects = await projectService.getProjects();
        if (this.projects.length > 0) {
          await this.$nextTick();

          const savedProject = this.loadCurrentProject();
          if (savedProject) {
            console.log('💾 Загружен сохраненный проект:', savedProject.name);
            // Загружаем задачи только для текущего проекта
            await this.loadProjectTasks(savedProject.id);
            this.currentProject = savedProject;
          } else {
            console.log('📁 Загружен первый проект:', this.projects[0].name);
            // Загружаем задачи только для первого проекта
            await this.loadProjectTasks(this.projects[0].id);
            this.currentProject = this.projects[0];
          }
        } else {
          console.log('📁 Нет проектов');
          this.currentProject = null;
        }

        this.generateTimeline();

      } catch (error) {
        console.error('Ошибка загрузки проектов:', error);
        this.showError('Не удалось загрузить проекты');
        this.generateTimeline();
      }
    },

    async loadProjectTasks(projectId) {
      // Загружает задачи только для указанного проекта (оптимизация)
      try {
        const tasks = await projectService.getProjectTasks(projectId);
        // Сортируем по позиции для правильного порядка
        tasks.sort((a, b) => (a.position || 0) - (b.position || 0));

        const project = this.projects.find(p => p.id === projectId);
        if (project) {
          project.tasks = tasks;
        }
        console.log(`📊 Загружено ${tasks.length} задач для проекта ${projectId}`);
      } catch (error) {
        console.error('Ошибка загрузки задач проекта:', error);
      }
    },

    async loadWorkers() {
      try {
        this.workers = await workerService.getWorkers();
      } catch (error) {
        console.error('Ошибка загрузки исполнителей:', error);
        this.showError('Не удалось загрузить исполнителей');
      }
    },

    saveCurrentProject(project) {
      if (project && project.id) {
        localStorage.setItem('currentProjectId', project.id.toString());
        console.log('💾 Сохранен проект:', project.id);
      }
    },

    loadCurrentProject() {
      try {
        const savedProjectId = localStorage.getItem('currentProjectId');
        console.log('💾 Пытаемся загрузить проект ID:', savedProjectId);
        
        if (savedProjectId && this.projects && this.projects.length > 0) {
          const projectId = parseInt(savedProjectId);
          const project = this.projects.find(p => p.id === projectId);
          if (project) {
            console.log('💾 Успешно загружен проект:', project.name);
            return project;
          } else {
            console.log('💾 Проект не найден, будет использован первый');
          }
        }
      } catch (error) {
        console.error('💾 Ошибка загрузки сохраненного проекта:', error);
      }
      return null;
    },

    async addProject() {
      const name = prompt('Введите название проекта:');
      if (!name) return;

      try {
        const newProject = await projectService.createProject({
          name: name,
          description: 'Новый проект'
        });
        // Оптимизация: добавляем проект локально
        newProject.tasks = [];
        this.projects.push(newProject);
        this.currentProject = newProject;
        this.saveCurrentProject(newProject);
        this.generateTimeline();
        this.showSuccess('Проект создан успешно');
        this.$emit('projectCreated');
      } catch (error) {
        console.error('Ошибка создания проекта:', error);
        this.showError('Не удалось создать проект');
      }
    },

    createNewProject() {
      this.addProject();
    },

    selectTask(task, event) {
      if (!task) {
        this.selectedTaskId = null;
        this.selectedTaskIds = [];
        return;
      }

      const tasks = this.currentProject?.tasks || [];
      const currentIndex = tasks.findIndex(t => t.id === task.id);

      if (event?.shiftKey && this.selectedTaskId) {
        const anchorIndex = tasks.findIndex(t => t.id === this.selectedTaskId);
        if (anchorIndex !== -1 && currentIndex !== -1) {
          const start = Math.min(anchorIndex, currentIndex);
          const end = Math.max(anchorIndex, currentIndex);
          this.selectedTaskIds = tasks.slice(start, end + 1).map(t => t.id);
          this.selectedTaskId = task.id;
          return;
        }
      }

      if (event?.ctrlKey || event?.metaKey) {
        const ids = new Set(this.selectedTaskIds || []);
        if (ids.has(task.id)) {
          ids.delete(task.id);
        } else {
          ids.add(task.id);
        }
        this.selectedTaskIds = tasks.filter(t => ids.has(t.id)).map(t => t.id);
        this.selectedTaskId = this.selectedTaskIds.length ? task.id : null;
        return;
      }

      this.selectedTaskId = task.id;
      this.selectedTaskIds = [task.id];
    },

    async createOperationBlock() {
      if (!this.currentProject) return;

      const selectedIds = this.selectedTaskIds.length > 0
        ? this.selectedTaskIds
        : (this.selectedTaskId ? [this.selectedTaskId] : []);

      if (!selectedIds.length) {
        this.showError('\u0412\u044b\u0434\u0435\u043b\u0438\u0442\u0435 \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u0438 \u0434\u043b\u044f \u0431\u043b\u043e\u043a\u0430.');
        return;
      }

      const tasks = this.currentProject.tasks || [];
      const selectedTasks = tasks.filter(task => selectedIds.includes(task.id));
      if (!selectedTasks.length) {
        this.showError('\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043d\u0430\u0439\u0442\u0438 \u0432\u044b\u0434\u0435\u043b\u0435\u043d\u043d\u044b\u0435 \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u0438.');
        return;
      }

      const workerIds = new Set(selectedTasks.map(task => task.worker));
      if (workerIds.size !== 1) {
        this.showError('\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u0438 \u043e\u0434\u043d\u043e\u0433\u043e \u0440\u043e\u0431\u043e\u0442\u0430.');
        return;
      }

      const workerId = selectedTasks[0].worker;
      const workerName = this.workers.find(worker => worker.id === workerId)?.name || 'robot';

      const result = await Swal.fire({
        title: '\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0431\u043b\u043e\u043a\u0430',
        input: 'text',
        inputValue: `\u0411\u043b\u043e\u043a ${workerName}`,
        showCancelButton: true,
        confirmButtonText: 'OK',
        cancelButtonText: '\u041e\u0442\u043c\u0435\u043d\u0430',
        confirmButtonColor: '#198754',
        cancelButtonColor: '#6c757d',
        inputValidator: (value) => {
          if (!value || !value.trim()) {
            return '\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0431\u043b\u043e\u043a\u0430';
          }
          return null;
        }
      });

      if (!result.isConfirmed) return;

      const name = result.value.trim();
      const items = selectedTasks.map((task, index) => ({
        task: task.id,
        position: index
      }));

      try {
        await operationBlockService.createBlock({
          name: name,
          worker: workerId,
          source_project: this.currentProject.id,
          items: items
        });

        await Swal.fire({
          icon: 'success',
          title: '\u0411\u043b\u043e\u043a \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d',
          timer: 1500,
          showConfirmButton: false
        });

        this.selectedTaskId = null;
        this.selectedTaskIds = [];
      } catch (error) {
        console.error('Block create error:', error);
        this.showError('\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0441\u043e\u0437\u0434\u0430\u0442\u044c \u0431\u043b\u043e\u043a.');
      }
    },

    getSelectedTask() {
      if (!this.currentProject?.tasks) return null;
      const selectedId = this.selectedTaskId || this.selectedTaskIds[0];
      if (!selectedId) return null;
      return this.currentProject.tasks.find(task => task.id === selectedId) || null;
    },

    getSelectedTasks() {
      const ids = this.selectedTaskIds.length > 0
        ? this.selectedTaskIds
        : (this.selectedTaskId ? [this.selectedTaskId] : []);
      if (!ids.length) return [];
      const allTasks = (this.projects && this.projects.length > 0)
        ? this.projects.flatMap(project => project.tasks || [])
        : (this.currentProject?.tasks || []);
      const taskById = new Map(allTasks.map(task => [task.id, task]));
      return ids.map(id => taskById.get(id)).filter(Boolean);
    },

    copySelectedTask() {
      const tasks = this.getSelectedTasks();
      if (!tasks.length) {
        this.copiedTasks = [];
        return;
      }
      this.copiedTasks = tasks.map(task => JSON.parse(JSON.stringify(task)));
    },

    async pasteCopiedTask() {
      if (!this.currentProject || this.copiedTasks.length === 0) return;

      const baseTask = this.getSelectedTask();
      const baseIndex = baseTask && this.currentProject?.tasks
        ? this.currentProject.tasks.findIndex(task => task.id === baseTask.id)
        : -1;
      const basePosition = baseTask && baseTask.position !== null && baseTask.position !== undefined
        ? baseTask.position
        : null;
      const insertPosition = basePosition !== null
        ? basePosition + 1
        : (baseIndex >= 0 ? baseIndex + 1 : null);

      try {
        let startTime = baseTask?.finish_time;
        const createdTasks = [];

        for (let i = 0; i < this.copiedTasks.length; i += 1) {
          const sourceTask = this.copiedTasks[i];
          const duration = sourceTask.duration || 0;
          const rawName = sourceTask.name || '';
          const baseName = rawName.replace(/(\s*\(copy\)\s*)+$/i, '').trim();
          const taskData = {
            project: this.currentProject.id,
            name: baseName || rawName,
            worker: sourceTask.worker,
            color: sourceTask.color || '#3498db',
            duration: duration,
            dependencies: []
          };

          if (insertPosition !== null) {
            taskData.position = insertPosition + i;
          }

          if (startTime !== null && startTime !== undefined) {
            taskData.start_time = startTime;
            taskData.finish_time = startTime + duration;
            startTime = taskData.finish_time;
          }

          const createdTask = await taskService.createTask(taskData);
          createdTasks.push(createdTask);
          this.pushUndo({ type: 'create', taskId: createdTask.id });
        }

        // Оптимизация: добавляем задачи локально в правильную позицию
        if (!this.currentProject.tasks) {
          this.currentProject.tasks = [];
        }

        // Находим позицию для вставки (после выбранной задачи)
        let insertIndex = this.currentProject.tasks.length;
        if (baseTask) {
          // Находим индекс последней задачи с position < insertPosition
          const lastBeforeIndex = this.currentProject.tasks
            .map((t, i) => ({ task: t, index: i }))
            .filter(item => item.task.position < insertPosition)
            .sort((a, b) => b.task.position - a.task.position)[0];

          if (lastBeforeIndex) {
            insertIndex = lastBeforeIndex.index + 1;
          } else {
            insertIndex = 0; // Вставляем в начало, если нет задач с меньшей позиции
          }
        }

        // Вставляем задачи по одной, чтобы сохранить порядок
        createdTasks.forEach((task, i) => {
          this.currentProject.tasks.splice(insertIndex + i, 0, task);
        });

        this.generateTimeline();

        if (createdTasks.length > 0) {
          const lastCreatedId = createdTasks[createdTasks.length - 1].id;
          this.selectedTaskId = lastCreatedId;
          this.selectedTaskIds = [lastCreatedId];
        }
      } catch (error) {
        console.error('Copy task error:', error);
        this.showError('Could not paste task');
      }
    },

    async undoLastAction() {
      if (this.undoStack.length === 0) return;

      const action = this.undoStack.pop();
      this.isUndoing = true;

      try {
        if (action.type === 'update' && action.task) {
          await taskService.updateTask(action.task.id, action.task);
        } else if (action.type === 'create' && action.taskId) {
          await taskService.deleteTask(action.taskId);
        }

        await this.loadProjects();
        this.generateTimeline();
      } catch (error) {
        console.error('Undo error:', error);
        this.showError('Could not undo last action');
      } finally {
        this.isUndoing = false;
      }
    },

    async addWorker() {
      // Ввод имени исполнителя
      const nameResult = await Swal.fire({
        title: 'Добавить исполнителя',
        text: 'Введите имя исполнителя:',
        input: 'text',
        inputPlaceholder: 'Имя исполнителя',
        inputValidator: (value) => {
          if (!value) {
            return 'Имя исполнителя обязательно!';
          }
        },
        showCancelButton: true,
        confirmButtonText: 'Далее',
        cancelButtonText: 'Отмена',
        confirmButtonColor: '#007bff',
        cancelButtonColor: '#6c757d'
      });

      if (!nameResult.isConfirmed) return;

      const name = nameResult.value;

      // Ввод кода исполнителя
      const labelResult = await Swal.fire({
        title: 'Добавить исполнителя',
        text: 'Введите код исполнителя (2-5 символов):',
        input: 'text',
        inputPlaceholder: 'Код исполнителя',
        inputValidator: (value) => {
          if (!value) {
            return 'Код исполнителя обязателен!';
          }
          if (value.length < 2 || value.length > 5) {
            return 'Код исполнителя должен быть от 2 до 5 символов!';
          }
        },
        showCancelButton: true,
        confirmButtonText: 'Создать',
        cancelButtonText: 'Отмена',
        confirmButtonColor: '#28a745',
        cancelButtonColor: '#6c757d'
      });

      if (!labelResult.isConfirmed) return;

      const label = labelResult.value;
      
      try {
        await workerService.createWorker({
          name: name,
          label: label,
          color: getRandomColor(),
          note: ''
        });
        await this.loadWorkers();
        this.showSuccess('Исполнитель создан успешно');
      } catch (error) {
        console.error('Ошибка создания исполнителя:', error);
        this.showError('Не удалось создать исполнителя');
      }
    },

     async addTask(duration = 10) { // значение по умолчанию
      if (!this.currentProject) return;

      try {
        const defaultWorker = this.workers[0];
        const operationName = this.generateOperationName();

        // Показываем загрузку
        Swal.fire({
          title: 'Создание операции...',
          text: 'Пожалуйста, подождите',
          allowOutsideClick: false,
          didOpen: () => {
            Swal.showLoading();
          }
        });

        const createdTask = await taskService.createTask({
          project: this.currentProject.id,
          name: operationName,
          worker: defaultWorker.id,
          color: defaultWorker.color,
          duration: duration,
          dependencies: []
        });

        this.pushUndo({ type: 'create', taskId: createdTask.id });

        // Оптимизация: добавляем задачу локально вместо полной перезагрузки
        if (!this.currentProject.tasks) {
          this.currentProject.tasks = [];
        }
        this.currentProject.tasks.push(createdTask);

        // Сортируем по позиции
        this.currentProject.tasks.sort((a, b) => (a.position || 0) - (b.position || 0));

        this.generateTimeline();

        // Успешное создание
        Swal.fire({
          icon: 'success',
          title: 'Успешно!',
          text: 'Операция создана',
          confirmButtonText: 'OK',
          confirmButtonColor: '#198754',
          timer: 2000
        });

      } catch (error) {
        console.error('Ошибка создания операции:', error);

        Swal.fire({
          icon: 'error',
          title: 'Ошибка',
          text: error.message || 'Не удалось создать операцию',
          confirmButtonText: 'OK',
          confirmButtonColor: '#dc3545'
        });
      }
    },

    async updateTask(task) {
      console.log('🔄 Обновление задачи:', task);
      try {
        const previousTask = this.currentProject?.tasks?.find(t => t.id === task.id);
        if (!this.isUndoing && previousTask) {
          this.pushUndo({ type: 'update', task: JSON.parse(JSON.stringify(previousTask)) });
        }

        const response = await taskService.updateTask(task.id, task);
        console.log('✅ Задача обновлена:', response);
        // Оптимизация: обновляем задачу локально без перезагрузки
        this.updateTaskInCurrentProject(response);
        this.generateTimeline();
      } catch (error) {
        console.error('❌ Ошибка обновления операции:', error);
      }
    },

    async updateTaskTimes(task) {
      console.log('📤 ProjectPlanner: updateTaskTimes', task);
      
      const hasStartTime = task.start_time !== null && task.start_time !== undefined;
      const hasFinishTime = task.finish_time !== null && task.finish_time !== undefined;
      
      if (task.duration && (!hasStartTime || !hasFinishTime)) {
        await this.updateTask(task);
        return;
      }

      if (hasStartTime && hasFinishTime) {
        const conflicts = this.findTimeConflicts(task);
        if (conflicts.length > 0) {
          alert(`Ошибка! Исполнитель уже занят в это время операциями:\n${conflicts.map(c => `- "${c.name}" (${c.start_time}-${c.finish_time} сек)`).join('\n')}`);
          return;
        }
        
        const dependencyErrors = this.checkDependencies(task);
        if (dependencyErrors.length > 0) {
          alert(`Ошибка зависимостей:\n${dependencyErrors.join('\n')}`);
          return;
        }
        
        await this.updateTask(task);
      }
    },

    async deleteTask(taskId) {
      try {
        await taskService.deleteTask(taskId);
        // Оптимизация: удаляем задачу локально без перезагрузки
        if (this.currentProject?.tasks) {
          this.currentProject.tasks = this.currentProject.tasks.filter(t => t.id !== taskId);
        }
        this.generateTimeline();
        this.showSuccess('Операция удалена успешно');
      } catch (error) {
        console.error('Ошибка удаления операции:', error);
        this.showError('Не удалось удалить операцию');
      }
    },

    async addDependentTask(baseTask) {
      if (!this.currentProject) return;

      try {
        // Находим исполнителя базовой задачи
        const baseWorker = this.workers.find(w => w.id === baseTask.worker);
        const operationName = this.generateOperationName();
        const baseIndex = this.currentProject?.tasks
          ? this.currentProject.tasks.findIndex(task => task.id === baseTask.id)
          : -1;
        const basePosition = baseTask.position !== null && baseTask.position !== undefined
          ? baseTask.position
          : null;
        const insertPosition = basePosition !== null
          ? basePosition + 1
          : (baseIndex >= 0 ? baseIndex + 1 : null);

        const createdTask = await taskService.createTask({
          project: this.currentProject.id,
          name: operationName,
          worker: baseTask.worker,
          color: baseWorker?.color || getRandomColor(), // Берем цвет из исполнителя
          start_time: baseTask.finish_time,
          finish_time: baseTask.finish_time + 10,
          position: insertPosition,
          dependencies: []
        });

        this.pushUndo({ type: 'create', taskId: createdTask.id });

        // Оптимизация: добавляем задачу локально
        if (!this.currentProject.tasks) {
          this.currentProject.tasks = [];
        }
        this.currentProject.tasks.push(createdTask);

        // Сортируем по позиции для правильного отображения
        this.currentProject.tasks.sort((a, b) => (a.position || 0) - (b.position || 0));

        this.generateTimeline();
        this.showSuccess('Зависимая операция создана успешно');
      } catch (error) {
        console.error('Ошибка создания зависимой операции:', error);
        this.showError('Не удалось создать зависимую операцию');
      }
    },

    async updateWorkerColorFromCell(workerId, newColor) {
      try {
        // Обновляем цвет исполнителя
        const worker = this.workers.find(w => w.id === workerId);
        if (worker) {
          worker.color = newColor;
          await workerService.updateWorker(workerId, worker);
        }

        // Оптимизация: собираем все задачи для массового обновления
        const tasksToUpdate = this.currentProject.tasks.filter(task => task.worker === workerId);

        if (tasksToUpdate.length > 0) {
          // Подготавливаем данные для bulk обновления
          const tasksData = tasksToUpdate.map(task => ({
            id: task.id,
            color: newColor
          }));

          // Отправляем один bulk запрос вместо множества отдельных
          const updatedTasks = await taskService.bulkUpdate(tasksData, this.currentProject.id);

          // Обновляем локально из ответа
          updatedTasks.forEach(updatedTask => {
            const task = this.currentProject.tasks.find(t => t.id === updatedTask.id);
            if (task) {
              Object.assign(task, updatedTask);
            }
          });
        }

        this.generateTimeline();
      } catch (error) {
        console.error('Ошибка обновления цветов:', error);
        this.showError('Не удалось обновить цвет исполнителя');
      }
    },

    async updateWorkerColor(workerId, newColor) {
      if (!confirm('Обновить цвет всех операций этого исполнителя?')) return;

      await this.updateWorkerColorFromCell(workerId, newColor);
      this.showSuccess('Цвет исполнителя обновлен');
    },

    async updateDependencies(task, dependencyIds) {
      try {
        task.dependencies = dependencyIds;
        await this.updateTask(task);
      } catch (error) {
        console.error('Ошибка обновления зависимостей:', error);
        this.showError('Не удалось обновить зависимости');
      }
    },

    async addDependency(task, dependencyId) {
      if (!dependencyId) return;
      
      const currentDeps = task.dependencies || [];
      if (!currentDeps.includes(parseInt(dependencyId))) {
        const newDeps = [...currentDeps, parseInt(dependencyId)];
        await this.updateDependencies(task, newDeps);
      }
    },

    async removeDependency(task, dependencyId) {
      const currentDeps = task.dependencies || [];
      const newDeps = currentDeps.filter(id => id !== dependencyId);
      await this.updateDependencies(task, newDeps);
    },

    generateTimeline() {
      const defaultTimelineLength = this.maxTimelineSeconds || 60;
      
      if (!this.currentProject?.tasks?.length) {
        this.timelineSeconds = [];
        for (let seconds = 0; seconds <= defaultTimelineLength; seconds++) {
          this.timelineSeconds.push(seconds);
        }
        console.log('📊 Создана временная шкала по умолчанию:', this.timelineSeconds.length, 'секунд');
        return;
      }
      
      const maxFinishTime = this.getMaxFinishTime();
      const totalSeconds = Math.ceil(Math.max(maxFinishTime, this.maxTimelineSeconds, defaultTimelineLength) * 1.2);
      
      this.timelineSeconds = [];
      for (let seconds = 0; seconds <= totalSeconds; seconds++) {
        this.timelineSeconds.push(seconds);
      }
      
      console.log('📊 Создана временная шкала с операциями:', this.timelineSeconds.length, 'секунд');
    },

    updateTaskInCurrentProject(updatedTask) {
      if (!this.currentProject?.tasks) return;
      
      const taskIndex = this.currentProject.tasks.findIndex(t => t.id === updatedTask.id);
      if (taskIndex !== -1) {
        this.currentProject.tasks = [
          ...this.currentProject.tasks.slice(0, taskIndex),
          updatedTask,
          ...this.currentProject.tasks.slice(taskIndex + 1)
        ];
      }
    },

    getMaxFinishTime() {
      if (!this.currentProject?.tasks?.length) return 0;
      return Math.max(...this.currentProject.tasks.map(task => task.finish_time));
    },

    findTimeConflicts(task) {
      if (!this.currentProject?.tasks) return [];
      
      return this.currentProject.tasks.filter(otherTask => 
        otherTask.id !== task.id &&
        otherTask.worker === task.worker &&
        this.isTimeOverlap(task, otherTask)
      );
    },

    isTimeOverlap(task1, task2) {
      return !(task1.finish_time <= task2.start_time || task1.start_time >= task2.finish_time);
    },

    checkDependencies(task) {
      const errors = [];
      const dependencies = task.dependencies || [];
      
      dependencies.forEach(depId => {
        const dependency = this.currentProject.tasks.find(t => t.id === depId);
        if (dependency && task.start_time < dependency.finish_time) {
          errors.push(`Операция "${task.name}" должна начинаться после завершения "${dependency.name}" (${dependency.finish_time} сек)`);
        }
      });
      
      this.currentProject.tasks.forEach(otherTask => {
        const otherDeps = otherTask.dependencies || [];
        if (otherDeps.includes(task.id) && otherTask.start_time < task.finish_time) {
          errors.push(`Операция "${otherTask.name}" зависит от этой операции и начинается раньше её завершения`);
        }
      });
      
      return errors;
    },

    setupKeyboardShortcuts() {
      document.addEventListener('keydown', (event) => {
        const tagName = event.target?.tagName?.toLowerCase();
        if (tagName === 'input' || tagName === 'textarea' || tagName === 'select' || event.target?.isContentEditable) {
          return;
        }

        if ((event.ctrlKey || event.metaKey) && event.key === '=') {
          event.preventDefault();
          this.pixelsPerSecond = Math.min(this.pixelsPerSecond + 5, 50);
        }
        if ((event.ctrlKey || event.metaKey) && event.key === '-') {
          event.preventDefault();
          this.pixelsPerSecond = Math.max(this.pixelsPerSecond - 5, 5);
        }
        if ((event.ctrlKey || event.metaKey) && event.key === '0') {
          event.preventDefault();
          this.pixelsPerSecond = 20;
        }
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'c') {
          event.preventDefault();
          this.copySelectedTask();
        }
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'v') {
          event.preventDefault();
          this.pasteCopiedTask();
        }
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z') {
          event.preventDefault();
          this.undoLastAction();
        }
      });
    },

    showError(message) {
      alert(`❌ ${message}`);
    },

    showSuccess(message) {
      console.log(`✅ ${message}`);
    },

    pushUndo(action) {
      if (this.isUndoing) return;
      this.undoStack.push(action);
      if (this.undoStack.length > 50) {
        this.undoStack.shift();
      }
    },

    getErrorMessage(error) {
      if (error.response?.data) {
        return typeof error.response.data === 'string' 
          ? error.response.data 
          : JSON.stringify(error.response.data);
      }
      return error.message || 'Неизвестная ошибка';
    },

    async addTaskFromExisting({ task, project }) {
      if (!this.currentProject) return;

      try {
        // Находим исполнителя копируемой задачи
        const worker = this.workers.find(w => w.id === task.worker);

        const createdTask = await taskService.createTask({
          project: this.currentProject.id,
          name: task.name,
          worker: task.worker,
          color: worker?.color || task.color,
          duration: task.duration,
          dependencies: []
        });

        // Оптимизация: добавляем задачу локально
        if (!this.currentProject.tasks) {
          this.currentProject.tasks = [];
        }
        this.currentProject.tasks.push(createdTask);

        // Сортируем по позиции
        this.currentProject.tasks.sort((a, b) => (a.position || 0) - (b.position || 0));

        this.generateTimeline();
        this.showSuccess(`Операция "${task.name}" скопирована из проекта "${project.name}"`);
      } catch (error) {
        console.error('Ошибка копирования операции:', error);
        this.showError('Не удалось скопировать операцию');
      }
    },

    async addTaskFromTemplate(template) {
      // Реализация по необходимости
    },

    async exportToExcel() {
      // Реализация по необходимости
    },

    generateOperationName() {
      const operationCount = this.currentProject?.tasks?.length || 0;
      return `Операция ${operationCount + 1}`;
    }
  }
}
</script>

<style>
@import '../styles/main.css';
</style>
