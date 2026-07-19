<template>
  <div class="actions-cell">
    <div class="actions-buttons">
      <button
        @click="confirmDelete"
        class="btn btn-sm action-btn"
        title="Удалить операцию"
      >
        <div class="icon-delete-container">
          <span class="icon-delete-symbol">✕</span>
        </div>
      </button>
      <button
        @click="$emit('addDependentTask', task)"
        class="btn btn-sm action-btn"
        title="Добавить следующую операцию"
      >
        <div class="icon-add-container">
          <span class="icon-add-symbol">+</span>
        </div>
      </button>
    </div>
  </div>
</template>

<script>
import Swal from 'sweetalert2'

export default {
  name: 'ActionsCell',
  props: {
    task: Object,
    column: Object,
    workers: Array,
    currentProject: Object
  },
  emits: ['deleteTask', 'addDependentTask'],
  methods: {
    async confirmDelete() {
      const result = await Swal.fire({
        title: 'Вы уверены?',
        text: `Вы собираетесь удалить операцию "${this.task.name}". Это действие нельзя отменить.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Да, удалить!',
        cancelButtonText: 'Отмена'
      })

      if (result.isConfirmed) {
        this.$emit('deleteTask', this.task.id)
        Swal.fire(
          'Удалено!',
          'Операция была успешно удалена.',
          'success'
        )
      }
    }
  }
}
</script>