<template>
  <div class="excel-grid-container">
    <!-- Excel-подобное поле для отображения полного названия -->
    <div 
      class="excel-display" 
      :class="{ 
        show: excelDisplay.show,
        'long-text': excelDisplay.class === 'long-text',
        'very-long-text': excelDisplay.class === 'very-long-text'
      }"
      :style="excelDisplay.style"
    >
      {{ excelDisplay.text }}
    </div>

    <!-- Уведомление об экспорте -->
    <div v-if="exportNotification.show" class="export-notification" :class="exportNotification.type">
      <div class="notification-content">
        <span class="notification-icon">
          <span v-if="exportNotification.type === 'loading'">...</span>
          <span v-else-if="exportNotification.type === 'success'">OK</span>
          <span v-else-if="exportNotification.type === 'error'">X</span>
        </span>
        <span class="notification-text">{{ exportNotification.message }}</span>
        <button v-if="exportNotification.type !== 'loading'" @click="exportNotification.show = false" class="notification-close">
          ×
        </button>
      </div>
    </div>

    <!-- Панель управления -->
    <div class="control-panel">
      <div class="header-row mb-3">
        <h3 class="mb-0">Циклограммус</h3>
      </div>

      <div class="controls-row">
        <button @click="$emit('addProject')" class="btn btn-primary me-2">Новый проект</button>
        
        <!-- Кнопка добавления операции -->
        <div class="btn-group me-2">
          <button @click="showTaskModal = true" class="btn btn-success" :disabled="!currentProject">
            Добавить операцию
          </button>
        </div>
        
        <button @click="$emit('addWorker')" class="btn btn-info me-2">
          Добавить исполнителя
        </button>

        <!-- Кнопка переключения панели масштабирования -->
        <button
          @click="showZoomPanel = !showZoomPanel"
          class="btn btn-outline-secondary"
          :class="{ active: showZoomPanel }"
        >
          Масштаб
        </button>

        

        <button
          @click="exportToExcel"
          class="btn btn-success"
          :disabled="!currentProject || !currentProject.tasks || currentProject.tasks.length === 0 || isExporting"
          title="Экспортировать циклограмму в Excel"
        >
          <span v-if="isExporting" class="spinner-border spinner-border-sm me-2" role="status"></span>
          {{ isExporting ? 'Экспорт...' : 'Экспорт в Excel' }}
        </button>
      </div>

      <!-- Панель масштабирования -->
      <div v-if="showZoomPanel" class="zoom-panel mt-3 p-3 bg-light rounded">
        <div class="zoom-controls-grid">
          <div class="zoom-slider-container">
            <label class="form-label">Масштаб времени: {{ timeScale }}x</label>
            <div class="d-flex align-items-center gap-3">
              <button @click="zoomOut" class="btn btn-outline-secondary btn-sm" title="Уменьшить масштаб">
                -
              </button>
              <input 
                type="range" 
                class="form-range zoom-slider"
                :min="minTimeScale"
                :max="maxTimeScale"
                :step="timeScaleStep"
                :value="timeScale"
                @input="setTimeScale(parseFloat($event.target.value))"
              >
              <button @click="zoomIn" class="btn btn-outline-secondary btn-sm" title="Увеличить масштаб">
                +
              </button>
            </div>
          </div>
          
          <div class="zoom-presets">
            <button @click="setTimeScale(0.5)" class="btn btn-outline-secondary btn-sm">50%</button>
            <button @click="setTimeScale(1)" class="btn btn-outline-secondary btn-sm">100%</button>
            <button @click="setTimeScale(2)" class="btn btn-outline-secondary btn-sm">200%</button>
            <button @click="fitToContent" class="btn btn-outline-primary btn-sm">Подогнать</button>
            <button @click="resetZoom" class="btn btn-outline-secondary btn-sm">Сбросить</button>
          </div>
          
          <div class="zoom-info">
            <small class="text-muted">
              Видимый диапазон: {{ timeRangeStart }}с - {{ timeRangeEnd }}с
              | Пикселей/сек: {{ Math.round(pixelsPerSecond) }}
            </small>
          </div>
        </div>
      </div>

      <!-- Список проектов -->
      <div class="mb-3">
        <label class="form-label">Текущий проект:</label>
        <select
          :value="currentProject?.id"
          @change="handleProjectChange($event.target.value)"
          class="form-select"
        >
          <option v-if="projects.length === 0" value="" disabled>Нет проектов</option>
          <option v-for="project in projects" :key="project.id" :value="project.id">
            {{ project.name }} ({{ project.tasks ? project.tasks.length : 0 }} операций)
          </option>
        </select>
      </div>
    </div>
    <div v-if="showDurationModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Создание новой операции</h5>
          <button type="button" class="btn-close" @click="cancelTaskCreation">×</button>
        </div>
        
        <div class="modal-body">
          <div class="mb-3">
            <label for="taskDuration" class="form-label">Длительность операции (в секундах):</label>
            <input 
              type="number" 
              id="taskDuration"
              class="form-control"
              v-model="newTaskDuration"
              min="1"
              placeholder="Введите длительность"
              @keyup.enter="confirmTaskDuration"
            >
          </div>
          
          <!-- Сообщение об ошибке -->
          <div v-if="showDurationError" class="alert alert-danger">
            Длительность должна быть положительным числом
          </div>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="cancelTaskCreation">Отмена</button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="confirmTaskDuration"
            :disabled="!isDurationValid"
          >
            Создать операцию
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно предупреждения об исполнителях -->
    <div v-if="showWorkerWarning" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Внимание</h5>
          <button type="button" class="btn-close" @click="showWorkerWarning = false">×</button>
        </div>
        
        <div class="modal-body">
          <p>Сначала добавьте исполнителей!</p>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" @click="showWorkerWarning = false">OK</button>
        </div>
      </div>
    </div>
    <!-- Модальное окно добавления операции -->
    <div v-if="showTaskModal && currentProject" class="modal-overlay">
      <div class="modal-content task-type-modal">
        <div class="modal-header">
          <h5 class="modal-title">Добавить операцию</h5>
          <button type="button" class="btn-close" @click="showTaskModal = false">×</button>
        </div>
        
        <div class="modal-body">
          <p class="modal-description">Выберите тип добавляемой операции:</p>
          
          <div class="task-type-options">
            <button
              @click="selectNewTask"
              class="task-type-btn new-task-btn"
            >
              <span class="task-type-content">
                <span class="task-type-title">Новая операция</span>
                <span class="task-type-description">Создать операцию с нуля</span>
              </span>
            </button>
            
            <button
              @click="selectExistingTask"
              class="task-type-btn existing-task-btn"
            >
              <span class="task-type-content">
                <span class="task-type-title">Из существующих</span>
                <span class="task-type-description">Выбрать из созданных операций</span>
              </span>
            </button>
          </div>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="showTaskModal = false">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно выбора существующих операций -->
    <div v-if="showExistingTaskModal && currentProject" class="modal-overlay">
      <div class="modal-content existing-tasks-modal">
        <div class="modal-header">
          <h5 class="modal-title">Выберите существующую операцию</h5>
          <button type="button" class="btn-close" @click="showExistingTaskModal = false">×</button>
        </div>
        
        <div class="modal-body">
          <div v-if="availableTasks.length === 0" class="no-tasks-message">
            <h6>Нет доступных операций</h6>
            <p>Создайте операции в других проектах, чтобы они появились здесь</p>
          </div>
          
          <div v-else>
            <label class="form-label">Выберите операцию для копирования:</label>
            <select v-model="selectedExistingTask" class="form-select custom-select">
              <option value="">Выберите операцию...</option>
              <option 
                v-for="task in availableTasks" 
                :key="task.id" 
                :value="task.id"
              >
                {{ task.name }} (Проект: {{ task.projectName }})
              </option>
            </select>
          </div>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="showExistingTaskModal = false">Отмена</button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="confirmExistingTask" 
            :disabled="!selectedExistingTask"
          >
            Добавить в проект
          </button>
        </div>
      </div>
    </div>


    <!-- Основная Excel-сетка -->
       <!-- Основная Excel-сетка с горизонтальным скроллом -->
    <div class="excel-main-grid" v-if="currentProject">
      <!-- Единая строка заголовков -->
      <div class="excel-header">
        <!-- Левая часть - таблица операций -->
        <div 
          v-for="column in leftColumns" 
          :key="column.key"
          class="excel-header-cell"
          :style="columnStyles[column.key]"
        >
          <div class="header-content">
            <span class="header-title">{{ column.title }}</span>
            <div 
              class="resize-handle"
              @mousedown="(event) => startLeftResize(column.key, event)"
              :title="`Изменить ширину колонки «${column.title}»`"
            ></div>
          </div>
        </div>

        <!-- Правая часть - секундная шкала -->
        <div class="excel-header-cell gantt-header-cell" ref="ganttHeader">
          <div class="time-scale-header" ref="timeScaleHeader">
            <div 
              v-for="seconds in visibleTimelineSeconds" 
              :key="seconds"
              class="time-scale-tick"
              :class="getTickClass(seconds)"
              :style="{ width: getSecondWidth() + 'px' }"
            >
              <span class="tick-label">{{ formatTickLabel(seconds) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Тело сетки с горизонтальным скроллом -->
      <div class="excel-body-container">
        <!-- Левая фиксированная часть -->
        <div class="excel-left-fixed">
          <div class="excel-body-left">
            <div
              v-for="task in currentProject.tasks"
              :key="task.id"
              class="excel-row-left"
              :class="{
                'selected-row': isTaskSelected(task.id),
                'dragging': draggedTaskId === task.id,
                'task-has-dependencies': task.dependencies && task.dependencies.length > 0
              }"
              :title="getTaskTooltip(task)"
              :style="{ backgroundColor: (task.color || '#3498db') + '20' }"
              draggable="true"
              @click="selectTask(task, $event)"
              @dragstart="handleDragStart($event, task)"
              @dragend="handleDragEnd"
              @dragover="handleDragOver($event, task)"
              @drop="handleDrop($event, task)"
            >
              <div 
                v-for="column in leftColumns" 
                :key="column.key"
                class="excel-cell"
                :style="{ width: getColumnWidth(column.key) + 'px', minWidth: getColumnMinWidth(column.key) + 'px' }"
              >
                <component
                  :is="getCellComponent(column.key)"
                  :task="task"
                  :column="column"
                  :workers="workers"
                  :currentProject="currentProject"
                  @updateTask="updateTaskField"
                  @updateTaskTime="updateTaskTimeField"
                  @addDependency="$emit('addDependency', task, $event)"
                  @removeDependency="$emit('removeDependency', task, $event)"
                  @openModal="openDependenciesModal"
                  @workerColorUpdated="handleWorkerColorUpdated"
                  @updateWorkerColor="handleUpdateWorkerColor"
                  @deleteTask="$emit('deleteTask', task.id)"
                  @addDependentTask="$emit('addDependentTask', task)"
                />
              </div>
            </div>
            
            <div v-if="!currentProject.tasks || currentProject.tasks.length === 0" class="excel-empty-row-left">
              <div class="empty-message">
                Нет операций. Добавьте первую операцию!
              </div>
            </div>
          </div>
        </div>

        <!-- Правая прокручиваемая часть -->
        <div class="excel-right-scrollable" ref="scrollableArea" @scroll="onHorizontalScroll">
          <div class="excel-body-right" :style="{ minWidth: totalGanttWidth + 'px' }">
            <div
              v-for="task in currentProject.tasks"
              :key="task.id"
              class="excel-row-right"
              :class="{
                'selected-row': isTaskSelected(task.id),
                'dragging': draggedTaskId === task.id,
                'task-has-dependencies': task.dependencies && task.dependencies.length > 0
              }"
              :title="getTaskTooltip(task)"
              :style="{ backgroundColor: (task.color || '#3498db') + '20' }"
              draggable="true"
              @click="selectTask(task, $event)"
              @dragstart="handleDragStart($event, task)"
              @dragend="handleDragEnd"
              @dragover="handleDragOver($event, task)"
              @drop="handleDrop($event, task)"
            >
              <div class="excel-cell gantt-cell" :style="{ width: totalGanttWidth + 'px' }">
                <GanttTimeline
                  :task="task"
                  :pixelsPerSecond="pixelsPerSecond"
                  :visibleSeconds="visibleTimelineSeconds"
                  :timeScale="timeScale"
                  :workers="workers"
                  :currentProject="currentProject"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Модальное окно для выбора существующих операций -->
    <div v-if="showExistingTaskSelect" class="modal-content">
      <h5>Выберите операцию для копирования</h5>
      <p class="text-muted small mb-2">
        Всего доступно операций: {{ totalTasksCount }}
      </p>
      <div class="mb-3">
        <select v-model="selectedExistingTask" class="form-select">
          <option value="">-- Выберите операцию --</option>
          <optgroup v-for="project in allProjectsWithTasks" :key="project.id" :label="`${project.name} (${project.tasks.length} операций)`">
            <option v-for="task in project.tasks" :key="task.id" :value="{task, project}">
              {{ task.name }} ({{ task.duration }} сек) - {{ getWorker(task.worker)?.name }}
            </option>
          </optgroup>
        </select>
      </div>
      <div class="d-flex gap-2">
        <button @click="confirmExistingTask" class="btn btn-primary btn-sm" :disabled="!selectedExistingTask">
          Выбрать операцию
        </button>
        <button @click="cancelExistingTask" class="btn btn-secondary btn-sm">Отмена</button>
      </div>
    </div>
  </div>
  <!-- Модальное окно зависимостей -->
  <div v-if="dependenciesModal.show && dependenciesModal.task" class="dropdown-overlay" @click="closeDependenciesModal">    <div class="dropdown-content" @click.stop>
      <div class="dropdown-body">
        <div v-if="getModalDependencyTasks().length > 0">
          <div class="section-title">
            <strong>Зависит от следующей операции:</strong>
          </div>
          <div class="dependency-list">
            <div 
              v-for="dep in getModalDependencyTasks()" 
              :key="dep.id" 
              class="dependency-item"
            >
              <div class="dependency-info">
                <strong>{{ dep.name }}</strong>
                <div class="dependency-details">
                  <span class="time-info">Время: {{ dep.start_time }}-{{ dep.finish_time }} сек</span>
                  <span class="duration-info">Длительность: {{ dep.finish_time - dep.start_time }} сек</span>
                </div>
              </div>
              <button
                @click="removeDependencyFromModal(dep.id)"
                class="btn btn-sm btn-outline-danger"
                title="Удалить зависимость"
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
        <div v-else class="no-dependencies">
          Нет зависимостей
        </div>
      </div>
      
      <div class="dropdown-footer">
        <button type="button" class="btn btn-secondary" @click="closeDependenciesModal">Закрыть</button>
      </div>
    </div>
  </div>
</template>

<script>
import TaskNameCell from './cells/TaskNameCell.vue'
import WorkerCell from './cells/WorkerCell.vue'
import TimeCell from './cells/TimeCell.vue'
import DurationCell from './cells/DurationCell.vue'
import DependenciesCell from './cells/DependenciesCell.vue'
import ColorCell from './cells/ColorCell.vue'
import ActionsCell from './cells/ActionsCell.vue'
import OrderCell from './cells/OrderCell.vue'
import GanttTimeline from './GanttTimeline.vue'
import Swal from 'sweetalert2';
export default {
  name: 'ExcelGrid',
  components: {
    GanttTimeline,
    TaskNameCell,
    WorkerCell,
    TimeCell,
    DurationCell,
    DependenciesCell,
    ColorCell,
    ActionsCell,
    OrderCell
  },
  props: {
    projects: Array,
    workers: Array,
    currentProject: Object,
    timelineSeconds: Array,
    selectedTaskId: Number,
    selectedTaskIds: Array
  },
  emits: [
    'update:currentProject',
    'addProject',
    'addTask',
    'addWorker',
    'updateTask',
    'updateTaskTimes',
    'deleteTask',
    'addDependentTask',
    'updateDependencies',
    'addDependency',
    'removeDependency',
    'addTaskFromTemplate',
    'addTaskFromExisting',
    'updateWorkerColor',
    'exportToExcel',
    'selectTask',
    'clearSelection',
    'createOperationBlock'
  ],
  data() {
    return {
      showAddTaskModal: false,
      showDurationModal: false,
      newTaskDuration: '10',
      showTaskModal: false,
      showExistingTaskModal: false,
      selectedExistingTask: null,
      showExistingTaskSelect: false,
      selectedExistingTask: null,
      showZoomPanel: false,
      isExporting: false,
      excelDisplay: {
        show: false,
        text: '',
        style: {},
        class: ''
      },
      taskNames: {},
      isExporting: false,
      exportNotification: {
        show: false,
        type: 'loading',
        message: ''
      },
      // Колонки левой части
      leftColumns: [
        { key: 'order', title: '№', width: 50, minWidth: 40 },
        { key: 'name', title: 'Операция', width: 250, minWidth: 20 },
        { key: 'worker', title: 'Исполнитель', width: 180, minWidth: 20 },
        { key: 'start_time', title: 'Старт', width: 100, minWidth: 20 },
        { key: 'finish_time', title: 'Финиш', width: 100, minWidth: 20 },
        { key: 'duration', title: 'Длит', width: 90, minWidth: 20 },
        { key: 'dependencies', title: 'Зависимости', width: 150, minWidth: 20 },
        { key: 'color', title: 'Цвет', width: 90, minWidth: 20 },
        { key: 'actions', title: 'Действия', width: 120, minWidth: 20 }
      ],
      isResizing: false,
      resizingColumnKey: null,
      startX: 0,
      startWidth: 0,
      // Масштабирование времени
      timeScale: 1.0,
      minTimeScale: 0.1,
      maxTimeScale: 5.0,
      timeScaleStep: 0.1,
      basePixelsPerSecond: 20,
      visibleTimeRange: null,
      // Drag and drop
      draggedTaskId: null,
      draggedOverTaskId: null,
      dragStartIndex: -1,
      isDragging: false,
      // Панель масштабирования
      showZoomPanel: false,
      // Горизонтальный скролл
      scrollPosition: 0,
      scrollThumbWidth: 100,
      dependenciesModal: {
        task: null,
        show: false
      }
    }
  },
  computed: {
    availableTasks() {
      if (!this.projects || this.projects.length === 0) return [];
      
      const allTasks = [];
      this.projects.forEach(project => {
        if (project.tasks && project.tasks.length > 0) {
          // Добавляем задачи с информацией о проекте
          project.tasks.forEach(task => {
            allTasks.push({
              ...task,
              projectName: project.name,
              projectId: project.id
            });
          });
        }
      });
      
      return allTasks;
    },
    columnStyles() {
      const styles = {};
      this.leftColumns.forEach(column => {
        styles[column.key] = {
          width: column.width + 'px',
          minWidth: Math.max(column.minWidth, 20) + 'px'
        };
      });
      return styles;
    },
    allProjectsWithTasks() {
      return this.projects.filter(project => project.tasks && project.tasks.length > 0);
    },
    totalTasksCount() {
      return this.allProjectsWithTasks.reduce((total, project) => total + project.tasks.length, 0);
    },
    visibleTimelineSeconds() {
      if (!this.timelineSeconds || this.timelineSeconds.length === 0) return [];
      
      // Показываем все секунды, скролл будет управлять видимой областью
      return this.timelineSeconds;
    },
    timeRangeStart() {
      return Math.floor(this.scrollPosition / this.pixelsPerSecond);
    },
    timeRangeEnd() {
      const containerWidth = this.$refs.scrollableArea ? this.$refs.scrollableArea.clientWidth : 800;
      return Math.floor((this.scrollPosition + containerWidth) / this.pixelsPerSecond);
    },
    // Пикселей в секунду с учетом масштаба
    pixelsPerSecond() {
      return this.basePixelsPerSecond * this.timeScale;
    },
    // Общая ширина диаграммы
    totalGanttWidth() {
      if (!this.timelineSeconds.length) return 0;
      return this.timelineSeconds.length * this.pixelsPerSecond;
    },
    isDurationValid() {
      const duration = parseInt(this.newTaskDuration);
      return !isNaN(duration) && duration > 0;
    }
  },
  watch: {
    currentProject: {
      handler() {
        this.updateScrollThumb();
      },
      deep: true
    },
    timeScale() {
      this.$nextTick(() => {
        this.updateScrollThumb();
      });
    },
    scrollPosition() {
      this.syncScroll();
    }
  },
  mounted() {
    this.setupHorizontalScroll();
    this.updateScrollThumb();
  },
  methods: {
    selectTask(task, event) {
      this.$emit('selectTask', task, event);
    },
    isTaskSelected(taskId) {
      if (Array.isArray(this.selectedTaskIds) && this.selectedTaskIds.length > 0) {
        return this.selectedTaskIds.includes(taskId);
      }
      return this.selectedTaskId === taskId;
    },
    selectNewTask() {
      this.showTaskModal = false;
      this.addNewTask();
    },
    
    selectExistingTask() {
      this.showTaskModal = false;
      this.showExistingTaskModal = true;
    },
    openDependenciesModal(task) {
      this.dependenciesModal.task = task;
      this.dependenciesModal.show = true;
    },

    closeDependenciesModal() {
      this.dependenciesModal.task = null;
      this.dependenciesModal.show = false;
    },

    getModalDependencyTasks() {
      if (!this.dependenciesModal.task || !this.currentProject?.tasks) return [];
      const dependencies = this.dependenciesModal.task.dependencies || [];
      return this.currentProject.tasks.filter(t => dependencies.includes(t.id));
    },

    removeDependencyFromModal(depId) {
      if (this.dependenciesModal.task) {
        this.$emit('removeDependency', this.dependenciesModal.task, depId);
      }
    },
    // МАСШТАБИРОВАНИЕ ВРЕМЕНИ
    setTimeScale(scale) {
      this.timeScale = Math.max(this.minTimeScale, Math.min(scale, this.maxTimeScale));
      this.updateScrollThumb();
    },
    
    zoomIn() {
      this.setTimeScale(this.timeScale + this.timeScaleStep);
    },
    
    zoomOut() {
      this.setTimeScale(this.timeScale - this.timeScaleStep);
    },
    
    resetZoom() {
      this.setTimeScale(1.0);
      this.scrollPosition = 0;
    },
    
    fitToContent() {
      if (!this.currentProject?.tasks?.length) return;
      
      const maxFinishTime = this.getMaxFinishTime();
      if (maxFinishTime === 0) return;
      
      // Вычисляем оптимальный масштаб чтобы вместить все задачи
      const containerWidth = this.$refs.scrollableArea ? this.$refs.scrollableArea.clientWidth : 800;
      const requiredWidth = maxFinishTime * this.basePixelsPerSecond;
      const optimalScale = Math.max(
        this.minTimeScale,
        Math.min(containerWidth / requiredWidth, this.maxTimeScale)
      );
      
      this.setTimeScale(optimalScale);
      this.scrollPosition = 0;
    },
    
    getMaxFinishTime() {
      if (!this.currentProject?.tasks?.length) return 0;
      return Math.max(...this.currentProject.tasks.map(task => task.finish_time || 0));
    },

    // ГОРИЗОНТАЛЬНЫЙ СКРОЛЛ
    setupHorizontalScroll() {
      // Инициализация скролла
      this.$nextTick(() => {
        this.updateScrollThumb();
      });
    },
    
    onHorizontalScroll(event) {
      const scrollTrack = event.target;
      const scrollWidth = scrollTrack.scrollWidth - scrollTrack.clientWidth;
      const scrollLeft = scrollTrack.scrollLeft;
      
      if (scrollWidth > 0) {
        this.scrollPosition = (scrollLeft / scrollWidth) * (this.totalGanttWidth - (this.$refs.scrollableArea?.clientWidth || 800));
      }
    },
    
    syncScroll() {
      if (this.$refs.timeScaleHeader && this.$refs.scrollableArea) {
        this.$refs.timeScaleHeader.scrollLeft = this.scrollPosition;
        this.$refs.scrollableArea.scrollLeft = this.scrollPosition;
      }
    },
    
    updateScrollThumb() {
      this.$nextTick(() => {
        const containerWidth = this.$refs.scrollableArea ? this.$refs.scrollableArea.clientWidth : 800;
        const visibleRatio = containerWidth / this.totalGanttWidth;
        this.scrollThumbWidth = Math.max(50, visibleRatio * 300); // Минимальная ширина 50px
      });
    },
    getTickClass(seconds) {
      const classes = [];
      if (seconds % 60 === 0) {
        classes.push('minute-tick');
      } else if (seconds % 30 === 0) {
        classes.push('half-minute-tick');
      } else if (seconds % 10 === 0) {
        classes.push('major-tick');
      }
      return classes;
    },
    getSecondWidth() {
      return this.pixelsPerSecond;
    },
    formatTickLabel(seconds) {
      const effectivePPS = this.getSecondWidth();
      if (effectivePPS < 8) {
        if (seconds % 60 === 0) return `${seconds/60}m`;
        if (seconds % 30 === 0) return `${seconds}s`;
        return '';
      } else if (effectivePPS < 15) {
        if (seconds % 10 === 0) return seconds;
        return '';
      } else {
        return seconds;
      }
    },
    getCellComponent(columnKey) {
      const components = {
        'order': 'OrderCell',
        'name': 'TaskNameCell',
        'worker': 'WorkerCell', 
        'start_time': 'TimeCell',
        'finish_time': 'TimeCell',
        'duration': 'DurationCell',
        'dependencies': 'DependenciesCell',
        'color': 'ColorCell',
        'actions': 'ActionsCell'
      };
      return components[columnKey];
    },

    getColumnWidth(columnKey) {
      const column = this.leftColumns.find(col => col.key === columnKey);
      return column ? column.width : 100;
    },

    getColumnMinWidth(columnKey) {
      const column = this.leftColumns.find(col => col.key === columnKey);
      const baseMinWidth = column ? column.minWidth : 80;
      // Гарантируем, что минимальная ширина не меньше ширины ползунка
      return Math.max(baseMinWidth, 16);
    },


    startLeftResize(columnKey, event) {
      event.preventDefault();
      event.stopPropagation();
      
      this.isResizing = true;
      this.resizingColumnKey = columnKey;
      this.startX = event.clientX;
      
      const column = this.leftColumns.find(col => col.key === columnKey);
      this.startWidth = column.width;
      
      // Добавляем класс для принудительного ограничения ширины
      const headerCell = event.target.closest('.excel-header-cell');
      if (headerCell) {
        headerCell.classList.add('resizing-column');
        
        // Находим соответствующие ячейки в теле таблицы через refs
        this.$nextTick(() => {
          const columnIndex = this.leftColumns.findIndex(col => col.key === columnKey);
          if (this.$refs.excelBodyLeft) {
            const bodyCells = this.$refs.excelBodyLeft.querySelectorAll(`.excel-cell:nth-child(${columnIndex + 1})`);
            bodyCells.forEach(cell => cell.classList.add('resizing-column'));
          }
        });
      }
      
      document.addEventListener('mousemove', this.handleLeftResize);
      document.addEventListener('mouseup', this.stopLeftResize);
      
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    },
    
    handleLeftResize(event) {
      if (!this.isResizing) return;
      
      const deltaX = event.clientX - this.startX;
      const column = this.leftColumns.find(col => col.key === this.resizingColumnKey);
      const resizeHandleWidth = 16;
      const minAllowedWidth = Math.max(column.minWidth, resizeHandleWidth);
      const newWidth = Math.max(this.startWidth + deltaX, minAllowedWidth);
      
      column.width = newWidth;
    },
    
    stopLeftResize(event) {
      this.isResizing = false;
      this.resizingColumnKey = null;
      
      if (this.$refs.excelBodyLeft) {
        const resizingColumns = this.$refs.excelBodyLeft.querySelectorAll('.resizing-column');
        resizingColumns.forEach(el => el.classList.remove('resizing-column'));
      }
      
      const headerCells = document.querySelectorAll('.excel-header-cell.resizing-column');
      headerCells.forEach(el => el.classList.remove('resizing-column'));
      
      document.removeEventListener('mousemove', this.handleLeftResize);
      document.removeEventListener('mouseup', this.stopLeftResize);
      
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    },

    autoScale() {
      if (!this.currentProject?.tasks?.length) return;
      
      const maxFinishTime = this.getMaxFinishTime();
      const containerWidth = 800;
      const optimalScale = Math.max(
        this.minScale,
        Math.min(containerWidth / maxFinishTime, this.maxScale)
      );
      
      this.$emit('update:pixelsPerSecond', Math.round(optimalScale));
    },
    
    resetScale() {
      this.$emit('update:pixelsPerSecond', this.defaultScale);
    },

    getMaxFinishTime() {
      if (!this.currentProject?.tasks?.length) return 0;
      return Math.max(...this.currentProject.tasks.map(task => task.finish_time));
    },

    handleProjectChange(projectId) {
      const selectedProject = this.projects.find(p => p.id === parseInt(projectId));
      if (selectedProject) {
        this.$emit('update:currentProject', selectedProject);
        this.$emit('projectChanged', selectedProject);
      }
    },

    updateTaskField(task, field, value) {
      const updatedTask = { ...task, [field]: value };
      this.$emit('updateTask', updatedTask);
    },

    updateTaskTimeField(task, field, value) {
      console.log('📤 ExcelGrid: updateTaskTimeField', { task: task.name, field, value });
      
      let numValue;
      
      if (value === '' || value === null || value === undefined) {
        numValue = null;
      } else {
        numValue = parseInt(value);
        if (isNaN(numValue)) {
          numValue = null;
        }
      }
      
      const updatedTask = { 
        ...task, 
        [field]: numValue
      };
      
      console.log('📤 ExcelGrid: отправка обновленной задачи', updatedTask);
      this.$emit('updateTaskTimes', updatedTask);
    },

    updateTaskColor(task, color) {
      const updatedTask = { ...task, color: color };
      this.$emit('updateTask', updatedTask);
    },

    getWorker(workerId) {
      return this.workers.find(w => w.id === workerId);
    },

    async addNewTask() {
      this.showTaskOptions = false;
      
      // Проверка исполнителей
      if (this.workers.length === 0) {
        await Swal.fire({
          icon: 'warning',
          title: 'Необходимы исполнители',
          text: 'Сначала добавьте исполнителей!',
          confirmButtonText: 'OK',
          confirmButtonColor: '#3085d6',
        });
        return;
      }
      
      // Запрос длительности операции
      const { value: duration } = await Swal.fire({
        title: 'Создание новой операции',
        input: 'number',
        inputLabel: 'Длительность операции (в секундах)',
        inputPlaceholder: 'Введите длительность...',
        inputValue: '10',
        inputAttributes: {
          min: '1',
          step: '1'
        },
        showCancelButton: true,
        confirmButtonText: 'Создать',
        cancelButtonText: 'Отмена',
        confirmButtonColor: '#198754',
        cancelButtonColor: '#6c757d',
        inputValidator: (value) => {
          if (!value || isNaN(value) || parseInt(value) <= 0) {
            return 'Длительность должна быть положительным числом!';
          }
        }
      });
      
      if (duration) {
        // Передаем длительность вместе с событием
        this.$emit('addTask', parseInt(duration));
      }
    },
    confirmTaskDuration() {
      const duration = parseInt(this.newTaskDuration);
      if (!duration || isNaN(duration) || duration <= 0) {
        this.showDurationError = true;
        return;
      }
      
      this.createNewTask(duration);
      this.showDurationModal = false;
      this.newTaskDuration = '10';
    },
    async createNewTask(duration) {
      // Эмитируем событие родителю для создания задачи
      this.$emit('addTask', duration);
    },
    cancelTaskCreation() {
      this.showDurationModal = false;
      this.newTaskDuration = '10';
    },
    addExistingTask() {
        if (this.selectedExistingTask) {
          console.log('Добавляем существующую операцию:', this.selectedExistingTask);
          this.showExistingTaskModal = false;
          this.selectedExistingTask = null;
        }
    },
     async confirmExistingTask() {
      if (!this.selectedExistingTask) return;
      
      const selectedTask = this.availableTasks.find(task => task.id === this.selectedExistingTask);
      if (!selectedTask) return;
      
      const result = await Swal.fire({
        title: 'Добавить операцию?',
        html: `
          <p>Вы собираетесь добавить операцию:</p>
          <p><strong>${selectedTask.name}</strong></p>
          <p>из проекта: <strong>${selectedTask.projectName}</strong></p>
        `,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#198754',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Добавить',
        cancelButtonText: 'Отмена',
        reverseButtons: true
      });
      
      if (result.isConfirmed) {
        this.$emit('addTaskFromExisting', this.selectedExistingTask);
        this.showExistingTaskModal = false;
        this.selectedExistingTask = null;
        this.showTaskOptions = false;
      }
    },

    cancelExistingTask() {
      this.showExistingTaskSelect = false;
      this.selectedExistingTask = null;
    },

    async exportToExcel() {
      if (!this.currentProject || !this.currentProject.tasks || this.currentProject.tasks.length === 0) {
        this.showNotification('error', 'Нет операций для экспорта!');
        return;
      }

      this.isExporting = true;
      this.showNotification('loading', 'Формирование Excel файла...', false);
      
      try {
        await this.downloadExcelFile(this.currentProject.id);
        this.showNotification('success', 'Циклограмма успешно экспортирована! Файл скачивается...');
      } catch (error) {
        console.error('Ошибка при экспорте:', error);
        this.showNotification('error', error.message || 'Произошла ошибка при экспорте файла');
      } finally {
        this.isExporting = false;
      }
    },

    async downloadExcelFile(projectId) {
      try {
        const response = await fetch(`/api/projects/${projectId}/export_cyclogram/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          let errorMessage = 'Ошибка при экспорте';
          try {
            const errorData = await response.json();
            errorMessage = errorData.error || errorData.detail || errorMessage;
          } catch (e) {
            errorMessage = `Ошибка ${response.status}: ${response.statusText}`;
          }
          throw new Error(errorMessage);
        }

        const blob = await response.blob();
        
        if (blob.size === 0) {
          throw new Error('Получен пустой файл');
        }

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `gantt_chart_project_${projectId}.xlsx`;
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
      } catch (error) {
        console.error('Ошибка при скачивании файла:', error);
        throw error;
      }
    },

    showNotification(type, message, autoHide = true) {
      this.exportNotification = {
        show: true,
        type: type,
        message: message
      };

      if (autoHide) {
        const duration = type === 'loading' ? 0 : (type === 'success' ? 3000 : 5000);
        if (duration > 0) {
          setTimeout(() => {
            if (this.exportNotification.show) {
              this.exportNotification.show = false;
            }
          }, duration);
        }
      }
    },

    // Drag and Drop методы
    handleDragStart(event, task) {
      this.draggedTaskId = task.id;
      this.isDragging = true;
      this.dragStartIndex = this.currentProject.tasks.findIndex(t => t.id === task.id);

      // Устанавливаем данные для перетаскивания
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/html', task.id);

      // Добавляем визуальный эффект
      event.target.classList.add('dragging');
    },

    handleDragOver(event, task) {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';

      // Убираем предыдущий индикатор
      this.clearDragOverIndicators();

      this.draggedOverTaskId = task.id;

      // Добавляем визуальный индикатор
      const targetRow = event.currentTarget;
      targetRow.classList.add('drag-over');
    },

    handleDragEnd() {
      this.draggedTaskId = null;
      this.draggedOverTaskId = null;
      this.isDragging = false;
      this.dragStartIndex = -1;

      // Убираем визуальные эффекты
      document.querySelectorAll('.dragging').forEach(el => {
        el.classList.remove('dragging');
      });

      this.clearDragOverIndicators();
    },

    clearDragOverIndicators() {
      // Убираем все индикаторы drag-over
      document.querySelectorAll('.drag-over').forEach(el => {
        el.classList.remove('drag-over');
      });
      this.draggedOverTaskId = null;
    },

    getTaskTooltip(task) {
      if (!task.dependencies || task.dependencies.length === 0) {
        return `Перетащите для изменения порядка выполнения`;
      }

      const dependencyNames = task.dependencies.map(depId => {
        const depTask = this.currentProject.tasks.find(t => t.id === depId);
        return depTask ? depTask.name : `Задача ${depId}`;
      }).join(', ');

      return `Зависит от: ${dependencyNames}. При перетаскивании время будет скорректировано автоматически.`;
    },

    async handleDrop(event, targetTask) {
      event.preventDefault();

      this.clearDragOverIndicators();

      const draggedTaskId = this.draggedTaskId;
      const targetTaskId = targetTask.id;

      if (draggedTaskId === targetTaskId) {
        this.handleDragEnd();
        return;
      }

      // Получаем перетаскиваемую задачу
      const draggedTask = this.currentProject.tasks.find(t => t.id === draggedTaskId);
      const hasDependencies = draggedTask && draggedTask.dependencies && draggedTask.dependencies.length > 0;

      // Показываем предупреждение если задача имеет зависимости
      if (hasDependencies) {
        const result = await Swal.fire({
          title: 'Задача имеет зависимости',
          text: 'Время выполнения этой задачи будет автоматически скорректировано с учетом ее зависимостей. Продолжить?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Да, изменить порядок',
          cancelButtonText: 'Отмена',
          confirmButtonColor: '#007bff',
          cancelButtonColor: '#6c757d'
        });

        if (!result.isConfirmed) {
          this.handleDragEnd();
          return;
        }
      }

      // Получаем индексы задач
      const draggedIndex = this.currentProject.tasks.findIndex(t => t.id === draggedTaskId);
      const targetIndex = this.currentProject.tasks.findIndex(t => t.id === targetTaskId);

      // Создаем новый порядок задач
      const reorderedTasks = [...this.currentProject.tasks];
      const [removedTask] = reorderedTasks.splice(draggedIndex, 1);
      reorderedTasks.splice(targetIndex, 0, removedTask);

      // Пересчитываем время выполнения для всех задач
      const updatedTasks = this.recalculateTaskTimes(reorderedTasks);

      try {
        // Сначала сохраняем порядок задач
        const taskIds = updatedTasks.map(task => task.id);
        await this.reorderTasks(taskIds);

        // Затем обновляем время выполнения
        await this.bulkUpdateTasks(updatedTasks);

        // Обновляем локальный проект
        this.currentProject.tasks = updatedTasks;

        // Уведомляем родительский компонент
        this.$emit('projectChanged', this.currentProject);

        if (hasDependencies) {
          this.showSuccess('Порядок операций изменен с учетом зависимостей');
        } else {
          this.showSuccess('Порядок операций изменен');
        }
      } catch (error) {
        console.error('Ошибка при изменении порядка задач:', error);
        this.showError('Не удалось изменить порядок операций');
      }

      this.handleDragEnd();
    },

    recalculateTaskTimes(tasks) {
      // Пересчитываем время выполнения с учетом зависимостей
      const updatedTasks = [];
      const taskMap = new Map();

      // Создаем карту задач для быстрого доступа
      tasks.forEach(task => {
        taskMap.set(task.id, { ...task });
      });

      // Функция для получения максимального времени завершения зависимостей
      const getMaxDependencyFinishTime = (task, processedTasks) => {
        if (!task.dependencies || task.dependencies.length === 0) {
          return -1; // Нет зависимостей
        }

        let maxFinishTime = -1;
        task.dependencies.forEach(depId => {
          const depTask = taskMap.get(depId);
          if (depTask && processedTasks.has(depTask.id)) {
            maxFinishTime = Math.max(maxFinishTime, depTask.finish_time || 0);
          }
        });
        return maxFinishTime;
      };

      // Двухпроходный алгоритм:
      // 1. Сначала обрабатываем задачи без зависимостей
      // 2. Затем задачи с зависимостями, учитывая их ограничения

      const processedTasks = new Set();
      let currentTime = 0;

      // Первый проход: задачи без зависимостей или с уже обработанными зависимостями
      for (let i = 0; i < tasks.length; i++) {
        const originalTask = tasks[i];
        const task = taskMap.get(originalTask.id);

        if (processedTasks.has(task.id)) continue;

        const dependencyFinishTime = getMaxDependencyFinishTime(task, processedTasks);

        // Если все зависимости обработаны или их нет
        if (dependencyFinishTime >= 0 || (!task.dependencies || task.dependencies.length === 0)) {
          if (dependencyFinishTime >= 0) {
            // Есть зависимости - стартуем после их завершения
            task.start_time = dependencyFinishTime;
          } else {
            // Нет зависимостей - используем последовательный порядок
            task.start_time = currentTime;
          }

          task.finish_time = task.start_time + task.duration;
          currentTime = Math.max(currentTime, task.finish_time);

          updatedTasks.push(task);
          processedTasks.add(task.id);
        }
      }

      // Второй проход: задачи, зависимости которых еще не были обработаны
      // (случай циклических зависимостей или неправильного порядка)
      for (let i = 0; i < tasks.length; i++) {
        const originalTask = tasks[i];
        const task = taskMap.get(originalTask.id);

        if (processedTasks.has(task.id)) continue;

        // Для оставшихся задач - находим максимальное время зависимостей
        const dependencyFinishTime = getMaxDependencyFinishTime(task, processedTasks);

        if (dependencyFinishTime >= 0) {
          task.start_time = dependencyFinishTime;
        } else {
          // Если даже во втором проходе нет обработанных зависимостей,
          // ставим в конец последовательности
          task.start_time = currentTime;
        }

        task.finish_time = task.start_time + task.duration;
        currentTime = Math.max(currentTime, task.finish_time);

        updatedTasks.push(task);
        processedTasks.add(task.id);
      }

      return updatedTasks;
    },

    async reorderTasks(taskIds) {
      // Сохранение порядка задач
      try {
        const response = await fetch(`/api/tasks/reorder_tasks/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            task_ids: taskIds,
            project_id: this.currentProject.id
          })
        });

        if (!response.ok) {
          throw new Error('Ошибка переупорядочивания задач');
        }

        const result = await response.json();
        // Обновляем задачи локально из ответа
        if (this.currentProject?.tasks) {
          this.currentProject.tasks = result;
        }
        return result;
      } catch (error) {
        console.error('Ошибка при reorder:', error);
        throw error;
      }
    },

    async bulkUpdateTasks(tasks) {
      // Групповое обновление времени выполнения задач
      const tasksData = tasks.map(task => ({
        id: task.id,
        start_time: task.start_time,
        finish_time: task.finish_time,
        duration: task.duration
      }));

      try {
        const response = await fetch(`/api/tasks/bulk_update/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            tasks: tasksData,
            project_id: this.currentProject.id
          })
        });

        if (!response.ok) {
          throw new Error('Ошибка обновления задач');
        }

        const result = await response.json();
        // Обновляем задачи локально из ответа
        if (this.currentProject?.tasks) {
          // Обновляем каждую задачу в текущем проекте
          result.forEach(updatedTask => {
            const index = this.currentProject.tasks.findIndex(t => t.id === updatedTask.id);
            if (index !== -1) {
              this.currentProject.tasks[index] = updatedTask;
            }
          });
        }
        return result;
      } catch (error) {
        console.error('Ошибка при bulk update:', error);
        throw error;
      }
    },

    showSuccess(message) {
      // Показываем уведомление об успехе
      this.exportNotification = {
        show: true,
        type: 'success',
        message: message
      };
      setTimeout(() => {
        this.exportNotification.show = false;
      }, 3000);
    },

    showError(message) {
      // Показываем уведомление об ошибке
      this.exportNotification = {
        show: true,
        type: 'error',
        message: message
      };
    },

    async sortTasksByOrder() {
      if (!this.currentProject || !this.currentProject.tasks || this.currentProject.tasks.length === 0) {
        return;
      }

      try {
        // Сортируем задачи по времени выполнения
        const sortedTasks = [...this.currentProject.tasks].sort((a, b) => {
          const aTime = a.start_time !== null && a.start_time !== undefined ? a.start_time : 0;
          const bTime = b.start_time !== null && b.start_time !== undefined ? b.start_time : 0;
          return aTime - bTime;
        });

        // Пересчитываем время выполнения с учетом зависимостей
        const updatedTasks = this.recalculateTaskTimes(sortedTasks);

        // Сохраняем новый порядок и обновляем время
        const taskIds = updatedTasks.map(task => task.id);
        await this.reorderTasks(taskIds);
        await this.bulkUpdateTasks(updatedTasks);

        // Обновляем локальный проект
        this.currentProject.tasks = updatedTasks;

        // Уведомляем родительский компонент
        this.$emit('projectChanged', this.currentProject);

        this.showSuccess('Операции отсортированы по порядку выполнения');
      } catch (error) {
        console.error('Ошибка при сортировке задач:', error);
        this.showError('Не удалось отсортировать операции');
      }
    },

    handleWorkerColorUpdated(workerId, newColor) {
      // Обновляем цвет исполнителя в локальном массиве
      const workerIndex = this.workers.findIndex(w => w.id === workerId);
      if (workerIndex !== -1) {
        this.workers[workerIndex].color = newColor;
        // Отправляем событие наверх для обновления workers в ProjectPlanner
        this.$emit('updateWorkerColorFromCell', workerId, newColor);
        // Принудительно обновляем компонент
        this.$forceUpdate();
      }
    },

    handleUpdateWorkerColor(workerId, newColor) {
      // Для обратной совместимости с существующим методом
      this.handleWorkerColorUpdated(workerId, newColor);
    }
  }
}
</script>

<style scoped>
@import '../styles/excel-grid.css';
</style>
