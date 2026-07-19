<template>
  <div class="color-cell">
    <div class="color-display-container" :title="colorInfo">
      <div class="color-display" @click="toggleColorPicker" :class="{ active: showColorPicker }">
        <span
          class="color-preview"
          :style="{ backgroundColor: taskColor }"
        ></span>
        <small class="color-text">{{ workerLabel }}</small>
      </div>

    </div>

  </div>
</template>

<script>
import { workerService } from '../../services/api';
import Swal from 'sweetalert2';

export default {
  name: 'ColorCell',
  props: {
    task: Object,
    column: Object,
    workers: Array,
    currentProject: Object
  },
  emits: ['workerColorUpdated'],
  data() {
    return {
      colorPalette: [
        '#FF6B6B', '#FF8E53', '#FF9F43', '#FFE066', '#A8E6CF', '#78C5A8',
        '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF'
      ]
    }
  },
  computed: {
    currentWorker() {
      return this.workers.find(w => w.id === this.task.worker);
    },
    taskColor() {
      // Цвет всегда берется из исполнителя
      return this.currentWorker?.color || '#3498db';
    },
    workerLabel() {
      return this.currentWorker?.label || '';
    },
    colorInfo() {
      return this.currentWorker ?
        `Исполнитель: ${this.currentWorker.name}\nЦвет: ${this.currentWorker.color}\nНажмите для изменения цвета` :
        'Исполнитель не найден';
    }
  },
  data() {
    return {
      colorPalette: [
        '#FF6B6B', '#FF8E53', '#FF9F43', '#FFE066', '#A8E6CF', '#78C5A8',
        '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF'
      ]
    }
  },
  methods: {
    async toggleColorPicker() {
      // Создаем HTML для палитры цветов
      const colorButtons = this.colorPalette.map(color =>
        `<button class="color-swal-btn" style="background-color: ${color};" data-color="${color}"></button>`
      ).join('');

      const result = await Swal.fire({
        title: 'Выберите цвет',
        html: `
          <div class="color-swal-palette">
            ${colorButtons}
          </div>
        `,
        showCancelButton: true,
        confirmButtonText: 'Отмена',
        cancelButtonText: 'Закрыть',
        customClass: {
          popup: 'color-swal-popup',
          confirmButton: 'btn btn-secondary',
          cancelButton: 'btn btn-outline-secondary'
        },
        buttonsStyling: false,
        didOpen: () => {
          // Добавляем обработчики кликов на цветные кнопки
          document.querySelectorAll('.color-swal-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
              const color = e.target.getAttribute('data-color');
              this.selectColor(color);
              Swal.close();
            });
          });
        }
      });
    },
    async selectColor(color) {
      if (!this.currentWorker) return;

      try {
        // Обновляем цвет исполнителя
        await workerService.updateWorker(this.currentWorker.id, {
          ...this.currentWorker,
          color: color
        });

        // Обновляем все задачи этого исполнителя
        this.$emit('workerColorUpdated', this.currentWorker.id, color);

        this.showColorPicker = false;
      } catch (error) {
        console.error('Ошибка обновления цвета:', error);
      }
    }
  },
}
</script>

<style scoped>
.color-cell {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.color-display-container {
  position: relative;
}

.color-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  cursor: pointer;
  transition: all 0.2s ease;
}

.color-display:hover,
.color-display.active {
  background: #e9ecef;
  border-color: #dee2e6;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.color-preview {
  width: 20px;
  height: 20px;
  border-radius: 3px;
  border: 1px solid #ddd;
  flex-shrink: 0;
  transition: border-color 0.2s ease;
}

.color-display:hover .color-preview {
  border-color: #bbb;
}

.color-text {
  font-size: 11px;
  color: #495057;
  font-weight: 500;
}

/* Палитра цветов */
.color-picker {
  z-index: 999999;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  min-width: 120px;
}

.color-palette {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4px;
  padding: 8px;
}

.color-option {
  width: 24px;
  height: 24px;
  border-radius: 3px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s ease;
}

.color-option:hover {
  transform: scale(1.1);
  border-color: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.color-option.selected {
  border-color: #fff;
  box-shadow: 0 0 0 2px #007bff;
}

.color-picker-footer {
  padding: 8px 12px;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
}

.color-picker-footer .btn {
  font-size: 12px;
  padding: 4px 12px;
}

</style>