<template>
  <div class="worker-cell">
    <select 
      :value="task.worker" 
      @change="updateWorker($event.target.value)"
      class="excel-select"
    >
      <option v-for="worker in workers" :key="worker.id" :value="worker.id">
        {{ worker.label }} - {{ worker.name }}
      </option>
    </select>
  </div>
</template>

<script>
export default {
  name: 'WorkerCell',
  props: {
    task: Object,
    column: Object,
    workers: Array,
    currentProject: Object
  },
  methods: {
    updateWorker(workerId) {
      const worker = this.workers.find(w => w.id === parseInt(workerId));
      if (worker) {
        // При смене исполнителя автоматически меняется цвет!
        const updatedTask = {
          ...this.task,
          worker: parseInt(workerId),
          color: worker.color // ← Цвет берется из нового исполнителя
        };
        this.$emit('updateTask', updatedTask);
      }
    }
  }
}
</script>

<style scoped>
.worker-cell {
  width: 100%;
}

.excel-select {
  width: 100%;
  border: 1px solid #ced4da;
  border-radius: 4px;
  padding: 6px 8px;
  font-size: 14px;
  background: white;
  transition: border-color 0.15s ease;
}

.excel-select:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}
</style>