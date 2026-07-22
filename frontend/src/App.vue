<template>
  <div id="app">
    <!-- Показываем страницу входа если не авторизованы -->
    <Auth v-if="!isAuthenticated" @authSuccess="handleAuthSuccess" />

    <!-- Показываем главное приложение если авторизованы -->
    <div v-else class="main-container">
      <!-- Оверлей для шторки -->
      <div
        v-if="isSidebarOpen"
        class="sidebar-overlay"
        @click="closeSidebar"
      ></div>

      <!-- Боковая шторка -->
      <aside class="sidebar" :class="{ open: isSidebarOpen }">
        <div class="sidebar-header">
          <button @click="closeSidebar" class="close-btn">×</button>
        </div>
        <nav class="sidebar-nav">
          <button
            @click="goToProjects"
            class="sidebar-link"
          >
            Редактор
          </button>
          <a
            href="/admin/"
            class="sidebar-link"
            @click="closeSidebar"
            target="_self"
          >
            Админка
          </a>
          <button
            @click="goToProfile"
            class="sidebar-link"
          >
            Личный кабинет
          </button>
          <button
            @click="handleLogout"
            class="sidebar-link sidebar-link-logout"
          >
            Выйти
          </button>
        </nav>
      </aside>

      <main class="app-main">
        <ProjectPlanner
          v-if="currentPage === 'projects'"
          :initialProjectId="initialProjectId"
          @projectCreated="handleProjectCreated"
          @openSidebar="openSidebar"
          ref="projectPlanner"
        />
        <Profile
          v-if="currentPage === 'profile'"
          @openProject="handleOpenProjectFromProfile"
          @createProject="handleCreateProjectFromProfile"
          @openSidebar="openSidebar"
        />
      </main>
    </div>
  </div>
</template>

<script>
import ProjectPlanner from './components/ProjectPlanner.vue'
import Profile from './components/Profile.vue'
import Auth from './components/Auth.vue'
import { authService } from './services/api'

export default {
  name: 'App',
  components: {
    ProjectPlanner,
    Profile,
    Auth
  },
  data() {
    return {
      isAuthenticated: false,
      currentUser: null,
      currentPage: 'projects',
      initialProjectId: null,
      isSidebarOpen: false
    }
  },
  mounted() {
    this.checkAuth()
  },
  methods: {
    checkAuth() {
      this.isAuthenticated = authService.isAuthenticated()
      this.currentUser = authService.getCurrentUser()
    },

    handleAuthSuccess(user) {
      this.isAuthenticated = true
      this.currentUser = user
    },

    async handleLogout() {
      await authService.logout()
      this.isAuthenticated = false
      this.currentUser = null
    },

    handleOpenProjectFromProfile(projectId) {
      this.initialProjectId = projectId
      this.currentPage = 'projects'
    },

    handleCreateProjectFromProfile() {
      this.currentPage = 'projects'
      setTimeout(() => {
        if (this.$refs.projectPlanner) {
          this.$refs.projectPlanner.createNewProject()
        }
      }, 100)
    },

    handleProjectCreated() {
      console.log('Project created')
    },

    openSidebar() {
      this.isSidebarOpen = true
    },

    closeSidebar() {
      this.isSidebarOpen = false
    },

    goToProfile() {
      this.currentPage = 'profile'
      this.closeSidebar()
    },

    goToProjects() {
      this.currentPage = 'projects'
      this.closeSidebar()
    }
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

.main-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Sidebar стили */
.sidebar {
  position: fixed;
  top: 0;
  left: -300px;
  width: 280px;
  height: 100vh;
  background: white;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  transition: left 0.3s ease;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.sidebar.open {
  left: 0;
}

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
}

.close-btn {
  font-size: 28px;
  color: #666;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #0d6efd;
}

.sidebar-nav {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar-link {
  display: block;
  padding: 14px 20px;
  background: #f8f9fa;
  color: #333;
  border-radius: 8px;
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
  text-align: left;
}

.sidebar-link:hover {
  background: #0d6efd;
  color: white;
  transform: translateX(4px);
}

.sidebar-link-logout {
  margin-top: 10px;
  background: #fff5f5;
  color: #dc3545;
}

.sidebar-link-logout:hover {
  background: #dc3545;
  color: white;
}

.app-main {
  flex: 1;
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
