<template>
  <div class="gantt-timeline-container">
    <!-- Бар задачи -->
    <div 
      class="gantt-bar"
      :style="getTaskBarStyle(task)"
      :title="getTaskTooltip(task)"
    >
    </div>
  </div>
</template>

<script>
import { getContrastColor, darkenColor } from '../utils/helpers'

export default {
  name: 'GanttTimeline',
  props: {
    task: Object,
    pixelsPerSecond: Number,
    visibleSeconds: Array,
    timeScale: Number,
    workers: Array,
    currentProject: Object,
    isInSelectedBlock: Function
  },
  methods: {
    getTaskBarStyle(task) {
      const startSeconds = task.start_time || 0;
      const durationSeconds = (task.finish_time || 0) - startSeconds;
      
      const startOffset = startSeconds * this.pixelsPerSecond;
      const width = Math.max(durationSeconds * this.pixelsPerSecond, this.pixelsPerSecond);
      
      let backgroundColor;
      if (task.color && task.color !== '#000000') {
        backgroundColor = task.color;
      } else {
        const worker = this.getWorker(task.worker);
        backgroundColor = worker ? worker.color : '#3498db';
      }
      
      const hasDependencies = task.dependencies && task.dependencies.length > 0;
      
      return {
        left: `${startOffset}px`,
        width: `${width}px`,
        backgroundColor: backgroundColor,
        color: getContrastColor(backgroundColor),
        border: hasDependencies ? `3px solid #f39c12` : `2px solid ${darkenColor(backgroundColor, 20)}`,
        boxShadow: hasDependencies ? '0 0 8px rgba(243, 156, 18, 0.6)' : '0 2px 6px rgba(0,0,0,0.2)',
        fontSize: this.getFontSize(),
        minWidth: `${this.pixelsPerSecond}px`
      };
    },
    
    getFontSize() {
      if (this.pixelsPerSecond < 10) return '9px';
      if (this.pixelsPerSecond < 20) return '10px';
      if (this.pixelsPerSecond < 30) return '11px';
      return '12px';
    },
    
    getWorker(workerId) {
      return this.workers.find(w => w.id === workerId);
    },
    
    getWorkerName(workerId) {
      const worker = this.getWorker(workerId);
      return worker ? worker.name : 'Не назначен';
    },
    
    getTaskTooltip(task) {
      const worker = this.getWorker(task.worker);
      const workerName = worker ? worker.name : 'Не назначен';

      let tooltip = `${task.name}\nИсполнитель: ${workerName}\nВремя: ${task.start_time}-${task.finish_time}с\nДлительность: ${task.duration}с`;

      // Добавляем информацию о цикле работы, если операция входит в выбранный цикл
      if (this.isInSelectedBlock && this.isInSelectedBlock(task.id)) {
        tooltip += '\n\n🔄 Входит в выбранный цикл работы';
      }

      return tooltip;
    }
  }
}
</script>

<style scoped>
.gantt-timeline-container {
  position: relative;
  height: 100%;
  width: 100%;
  min-width: min-content;
  background: 
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent calc(var(--pixel-width, 20px) - 1px),
      #f8f9fa calc(var(--pixel-width, 20px) - 1px),
      #f8f9fa var(--pixel-width, 20px)
    );
}

.gantt-bar {
  position: absolute;
  height: 32px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  display: flex;
  align-items: center;
  top: 6px;
  transition: all 0.2s ease;
  z-index: 2;
}

.gantt-bar:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  z-index: 3;
}

.gantt-bar-label {
  padding: 4px 8px;
  flex-grow: 1;
  text-shadow: 1px 1px 1px rgba(0,0,0,0.3);
  min-width: max-content;
  overflow: hidden;
  text-align: center;
}

.gantt-bar-name {
  font-weight: 600;
  line-height: 1.2;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.gantt-bar-worker {
  opacity: 0.9;
  margin-bottom: 1px;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.9em;
}

.gantt-bar-time {
  opacity: 0.9;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.8em;
}
</style>