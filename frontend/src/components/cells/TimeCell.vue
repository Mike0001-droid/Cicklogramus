<template>
  <div class="time-cell">
    <input 
      type="number" 
      :value="getTaskValue()"
      @blur="updateTime($event.target.value)"
      class="excel-input number-input"
      :min="getMinValue()"
      :placeholder="getPlaceholder()"
      :title="getTitle()"
    >
  </div>
</template>

<script>
export default {
  name: 'TimeCell',
  props: {
    task: Object,
    column: Object,
    workers: Array,
    currentProject: Object
  },
  methods: {
    getTaskValue() {
      return this.task[this.column.key];
    },
    
    updateTime(value) {
      // Исправляем логику: 0 должно оставаться 0, а не становиться null
      let numValue;
      
      if (value === '' || value === null || value === undefined) {
        numValue = null;
      } else {
        numValue = parseInt(value);
        // Проверяем, что это число и оно не NaN
        if (isNaN(numValue)) {
          numValue = null;
        }
      }
      
      console.log(`🔄 Обновление ${this.column.key}:`, { input: value, result: numValue });
      this.$emit('updateTaskTime', this.task, this.column.key, numValue);
    },
    
    getMinValue() {
      return this.column.key === 'start_time' ? 0 : 1;
    },
    
    getPlaceholder() {
      return this.column.key === 'start_time' ? 'Авто' : 'Авто';
    },
    
    getTitle() {
      return this.column.key === 'start_time' 
        ? 'Опционально: секунда старта' 
        : 'Опционально: секунда финиша';
    }
  }
}
</script>

<style scoped>
.time-cell {
  width: 100%;
}

.number-input {
  width: 100%;
  border: 1px solid #ced4da;
  border-radius: 4px;
  padding: 6px 8px;
  font-size: 14px;
  background: white;
  text-align: center;
  transition: border-color 0.15s ease;
}

.number-input:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}
</style>