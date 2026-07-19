<template>
  <div id="app">
    <ProjectPlanner />
  </div>
</template>

<script>
import ProjectPlanner from './components/ProjectPlanner.vue'

export default {
  name: 'App',
  components: {
    ProjectPlanner
  }
}
</script>

<style>
/* Глобальные сбросы стилей */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  height: 100%;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
  line-height: 1.4;
  color: #333;
  background-color: #f5f5f5;
}

#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* Убираем стандартные стили для списков */
ul, ol {
  list-style: none;
}

/* Убираем стандартные стили для ссылок */
a {
  text-decoration: none;
  color: inherit;
}

/* Убираем стандартные стили для кнопок */
button {
  border: none;
  background: none;
  cursor: pointer;
  font-family: inherit;
}

/* Убираем стандартные стили для инпутов */
input, select, textarea {
  font-family: inherit;
  font-size: inherit;
  border: none;
  outline: none;
}

/* Утилитарные классы */
.text-center {
  text-align: center;
}

.text-left {
  text-align: left;
}

.text-right {
  text-align: right;
}

.d-flex {
  display: flex;
}

.flex-column {
  flex-direction: column;
}

.align-items-center {
  align-items: center;
}

.justify-content-center {
  justify-content: center;
}

.justify-content-between {
  justify-content: space-between;
}

.w-100 {
  width: 100%;
}

.h-100 {
  height: 100%;
}

.m-0 { margin: 0; }
.m-1 { margin: 0.25rem; }
.m-2 { margin: 0.5rem; }
.m-3 { margin: 1rem; }

.p-0 { padding: 0; }
.p-1 { padding: 0.25rem; }
.p-2 { padding: 0.5rem; }
.p-3 { padding: 1rem; }

.mt-1 { margin-top: 0.25rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 1rem; }

.mb-1 { margin-bottom: 0.25rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-3 { margin-bottom: 1rem; }

.ml-1 { margin-left: 0.25rem; }
.ml-2 { margin-left: 0.5rem; }
.ml-3 { margin-left: 1rem; }

.mr-1 { margin-right: 0.25rem; }
.mr-2 { margin-right: 0.5rem; }
.mr-3 { margin-right: 1rem; }

.pt-1 { padding-top: 0.25rem; }
.pt-2 { padding-top: 0.5rem; }
.pt-3 { padding-top: 1rem; }

.pb-1 { padding-bottom: 0.25rem; }
.pb-2 { padding-bottom: 0.5rem; }
.pb-3 { padding-bottom: 1rem; }

.pl-1 { padding-left: 0.25rem; }
.pl-2 { padding-left: 0.5rem; }
.pl-3 { padding-left: 1rem; }

.pr-1 { padding-right: 0.25rem; }
.pr-2 { padding-right: 0.5rem; }
.pr-3 { padding-right: 1rem; }

/* Анимации */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(100%);
}

/* Медиа-запросы для адаптивности */
@media (max-width: 1200px) {
  html {
    font-size: 13px;
  }
}

@media (max-width: 768px) {
  html {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  html {
    font-size: 11px;
  }
}

/* Стили для режима печати */
@media print {
  .no-print {
    display: none !important;
  }

  body {
    background: white !important;
  }
}
</style>
