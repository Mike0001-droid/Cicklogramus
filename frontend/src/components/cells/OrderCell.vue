<template>
  <div class="order-cell">
    <span class="order-number">{{ orderNumber }}</span>
  </div>
</template>

<script>
export default {
  name: 'OrderCell',
  props: {
    task: Object,
    column: Object,
    currentProject: Object
  },
  computed: {
    orderNumber() {
      if (!this.currentProject?.tasks) return 0;

      const taskIndex = this.currentProject.tasks.findIndex(t => t.id === this.task.id);
      return taskIndex + 1; // +1 потому что индексы начинаются с 0
    }
  }
}
</script>

<style scoped>
.order-cell {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.order-number {
  font-size: 14px;
  font-weight: 600;
  color: #495057;
  min-width: 20px;
  text-align: center;
}
</style>
