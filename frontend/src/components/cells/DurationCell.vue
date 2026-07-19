<template>
  <div class="duration-cell">
    <input 
      type="number" 
      :value="task.duration" 
      @blur="updateDuration($event.target.value)"
      class="excel-input number-input"
      min="1"
      title="Длительность операции в секундах"
    >
  </div>
</template>

<script>
export default {
  name: 'DurationCell',
  props: {
    task: Object,
    column: Object,
    workers: Array,
    currentProject: Object
  },
  methods: {
    updateDuration(value) {
      const duration = parseInt(value) || 1;
      this.$emit('updateTask', this.task, 'duration', duration);
    }
  }
}
</script>

<style scoped>
.duration-cell {
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