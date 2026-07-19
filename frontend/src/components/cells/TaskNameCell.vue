<template>
  <div class="task-name-cell">
    <input 
      :value="task.name"
      @input="handleInput($event)"
      @blur="updateTaskName"
      @focus="showExcelDisplay"
      class="excel-input task-name-input"
      placeholder="Название операции"
    >
  </div>
</template>

<script>
export default {
  name: 'TaskNameCell',
  props: {
    task: Object,
    column: Object,
    workers: Array,
    currentProject: Object
  },
  data() {
    return {
      tempName: ''
    }
  },
  methods: {
    handleInput(event) {
      this.tempName = event.target.value;
    },
    
    updateTaskName() {
      if (this.tempName && this.tempName !== this.task.name) {
        this.$emit('updateTask', this.task, 'name', this.tempName);
      }
      this.tempName = '';
    },
    
    showExcelDisplay(event) {
      this.tempName = this.task.name;
      // Можно добавить логику для показа excel-display если нужно
    }
  }
}
</script>

<style scoped>
.task-name-cell {
  width: 100%;
}

.task-name-input {
  width: 100%;
  border: 1px solid #ced4da;
  border-radius: 4px;
  padding: 6px 8px;
  font-size: 14px;
  background: white;
  transition: border-color 0.15s ease;
}

.task-name-input:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}
</style>