<template>
  <div class="dependencies-section">
    <!-- Текущие зависимости -->
    <div v-if="getDependencyTasks().length > 0" class="current-dependencies">
      <div class="dependencies-header">
        <small class="dependencies-label">Зависит от:</small>
        <button 
          class="btn btn-sm btn-outline-info view-details-btn"
          :title="getTooltipText"
          @click="openDependenciesModal"
        >
          👁️
        </button>
      </div>
      <!-- <div class="dependencies-list">
        <div v-for="dep in getDependencyTasks()" :key="dep.id" class="dependency-badge">
          <span class="badge bg-info">
            {{ getShortName(dep.name) }}
            <button @click="removeDependency(dep.id)" class="btn-close btn-close-white ms-1" style="font-size: 8px;"></button>
          </span>
        </div>
      </div> -->
    </div>
    
    <!-- Добавление новой зависимости -->
    <button
      v-if="getDependencyTasks().length === 0 && !isFirstTask"
      @click="openAddDependencyModal"
      class="btn btn-sm btn-outline-success add-dependency-btn"
      :disabled="getAvailableDependencies().length === 0"
      :title="getAvailableDependencies().length === 0 ? 'Нет доступных задач для добавления зависимости' : 'Добавить зависимость'"
    >
      ➕ Добавить
    </button>
  </div>
</template>

<script>
import Swal from 'sweetalert2';

export default {
  name: 'TaskDependencies',
  props: {
    task: Object,
    currentProject: Object
  },
  emits: ['addDependency', 'removeDependency', 'openModal'],
  data() {
    return {
    }
  },
  computed: {
    isFirstTask() {
      if (!this.currentProject?.tasks) return false;
      return this.currentProject.tasks[0]?.id === this.task.id;
    },

    getTooltipText() {
      if (this.isFirstTask) {
        return 'Первая операция не может иметь зависимости';
      }

      const deps = this.getDependencyTasks();
      if (deps.length === 0) {
        return 'Просмотреть зависимости';
      }
      const names = deps.map(dep => dep.name).join(', ');
      return `Зависимости: ${names}`;
    }
  },
  methods: {
    openDependenciesModal() {
      console.log('🔄 Открытие модалки для задачи:', this.task.name);
      this.$emit('openModal', this.task);
    },

    async openAddDependencyModal() {
      const availableTasks = this.getAvailableDependencies();

      if (availableTasks.length === 0) {
        await Swal.fire({
          title: 'Нет доступных задач',
          text: 'Все задачи уже добавлены в зависимости или нет подходящих задач.',
          icon: 'info',
          confirmButtonText: 'OK'
        });
        return;
      }

      // Создаем опции для SweetAlert с сортировкой по позиции
      const inputOptions = {};
      availableTasks.forEach(task => {
        const position = (task.position || 0) + 1; // Позиция с 1, а не с 0
        inputOptions[task.id] = `№${position}. ${task.name} (${task.start_time}-${task.finish_time}с)`;
      });

      const result = await Swal.fire({
        title: 'Добавить зависимость',
        text: `Выберите задачу, от которой будет зависеть "${this.task.name}":`,
        input: 'select',
        inputOptions: inputOptions,
        inputPlaceholder: 'Выберите задачу',
        showCancelButton: true,
        confirmButtonText: 'Добавить',
        cancelButtonText: 'Отмена',
        confirmButtonColor: '#28a745',
        cancelButtonColor: '#6c757d',
        customClass: {
          popup: 'dependency-swal-popup',
          title: 'dependency-swal-title',
          htmlContainer: 'dependency-swal-text',
          input: 'dependency-swal-select',
          confirmButton: 'dependency-swal-confirm',
          cancelButton: 'dependency-swal-cancel'
        },
        inputValidator: (value) => {
          if (!value) {
            return 'Пожалуйста, выберите задачу!';
          }
        }
      });

      if (result.isConfirmed && result.value) {
        this.$emit('addDependency', result.value);
      }
    },

    removeDependency(depId) {
      this.$emit('removeDependency', depId);
    },
    
    getAvailableDependencies() {
      if (!this.currentProject?.tasks) return [];
      const currentDeps = this.task.dependencies || [];

      return this.currentProject.tasks
        .filter(otherTask =>
          otherTask.id !== this.task.id && // Не можем зависеть от себя
          !currentDeps.includes(otherTask.id) // Не можем дублировать зависимости
        )
        .sort((a, b) => (a.position || 0) - (b.position || 0)); // Сортировка по порядку
    },
    
    getDependencyTasks() {
      if (!this.currentProject?.tasks) return [];
      const dependencies = this.task.dependencies || [];
      return this.currentProject.tasks.filter(t => dependencies.includes(t.id));
    },
    
    getShortName(name) {
      if (name.length <= 8) return name;
      return name.substring(0, 6) + '..';
    }
  }
}
</script>

<style scoped>
.dependencies-section {
  min-width: 120px;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
}

/* Единая строка для зависимостей */
.current-dependencies {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  min-height: 32px;
  flex-wrap: wrap;
}

.dependencies-header {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.dependencies-label {
  font-size: 11px !important;
  font-weight: 500;
  color: #495057 !important;
  white-space: nowrap;
}

.view-details-btn {
  padding: 1px 4px;
  font-size: 10px;
  border: none;
  background: transparent;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.dependencies-list {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  flex: 1;
  align-items: center;
}

.dependency-badge .badge {
  font-size: 8px;
  padding: 2px 4px;
  max-width: 55px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.add-dependency-btn {
  font-size: 11px;
  padding: 2px 6px;
  white-space: nowrap;
}

.add-dependency-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Стили для SweetAlert зависимостей */
.dependency-swal-popup {
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2) !important;
  border: none !important;
}

.dependency-swal-title {
  color: #2c3e50 !important;
  font-weight: 600 !important;
  font-size: 20px !important;
  margin-bottom: 8px !important;
}

.dependency-swal-text {
  color: #6c757d !important;
  font-size: 14px !important;
  margin-bottom: 20px !important;
}

.dependency-swal-select {
  border: 2px solid #e9ecef !important;
  border-radius: 8px !important;
  padding: 12px 16px !important;
  font-size: 14px !important;
  color: #495057 !important;
  background: #fff !important;
  transition: all 0.3s ease !important;
  min-width: 300px !important;
}

.dependency-swal-select:focus {
  border-color: #28a745 !important;
  box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1) !important;
  outline: none !important;
}

.dependency-swal-select option {
  padding: 8px !important;
  background: #fff !important;
  color: #495057 !important;
}

.dependency-swal-confirm {
  background: #28a745 !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 10px 24px !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  transition: all 0.3s ease !important;
}

.dependency-swal-confirm:hover {
  background: #218838 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3) !important;
}

.dependency-swal-cancel {
  background: #6c757d !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 10px 24px !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  transition: all 0.3s ease !important;
}

.dependency-swal-cancel:hover {
  background: #545b62 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3) !important;
}
</style>