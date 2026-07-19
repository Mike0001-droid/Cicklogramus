<template>
  <div class="profile-layout">
    <!-- Боковая панель -->
    <aside class="sidebar">
      <div class="sidebar-user">
        <div class="user-avatar">
          {{ userInitials }}
        </div>
        <div class="user-details">
          <h3 class="user-name">{{ currentUser?.username || 'Пользователь' }}</h3>
          <p class="user-email">{{ currentUser?.email || 'email@example.com' }}</p>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section">
          <div class="nav-section-title">Основное</div>
          <a href="#" class="nav-item active" @click.prevent>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M6 12a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm4 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm-4-4a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm4 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"/>
            </svg>
            Проекты
          </a>
          <a href="#" class="nav-item" @click.prevent="showSettings = !showSettings">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zM0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm8-6a6 6 0 1 0 0 12A6 6 0 0 0 8 2z"/>
            </svg>
            Настройки профиля
          </a>
        </div>
      </nav>

      <div class="sidebar-stats">
        <div class="stat-box">
          <div class="stat-number">{{ stats.projects }}</div>
          <div class="stat-label">Проектов</div>
        </div>
        <div class="stat-box">
          <div class="stat-number">{{ stats.tasks }}</div>
          <div class="stat-label">Задач</div>
        </div>
      </div>
    </aside>

    <!-- Основной контент -->
    <main class="main-content">
      <div class="content-header">
        <h1>Проекты</h1>
        <button @click="createNewProject" class="btn-new-project">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 2a.5.5 0 0 1 .5.5v5h5a.5.5 0 0 1 0 1h-5v5a.5.5 0 0 1-1 0v-5h-5a.5.5 0 0 1 0-1h5v-5A.5.5 0 0 1 8 2z"/>
          </svg>
          Новый проект
        </button>
      </div>

      <!-- Список проектов -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Загрузка проектов...</p>
      </div>

      <div v-else-if="projects.length === 0" class="empty-state">
        <svg width="64" height="64" viewBox="0 0 16 16" fill="#dbdbdb">
          <path d="M6 12a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm4 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm-4-4a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm4 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"/>
        </svg>
        <h3>У вас пока нет проектов</h3>
        <p>Создайте свой первый проект, чтобы начать работу</p>
        <button @click="createNewProject" class="btn-primary">Создать проект</button>
      </div>

      <div v-else class="projects-list">
        <div v-for="project in projects" :key="project.id" class="project-card" @click="openProject(project.id)">
          <div class="project-icon">
            {{ getProjectInitials(project.name) }}
          </div>
          <div class="project-info">
            <h3 class="project-name">{{ project.name }}</h3>
            <p class="project-description">{{ project.description || 'Описание отсутствует' }}</p>
            <div class="project-meta">
              <span class="project-tasks">{{ project.task_count || 0 }} задач</span>
              <span class="project-date">{{ formatDate(project.created_at) }}</span>
            </div>
          </div>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" class="project-arrow">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </div>
      </div>

      <!-- Модальное окно настроек -->
      <div v-if="showSettings" class="modal-overlay" @click.self="showSettings = false">
        <div class="modal">
          <div class="modal-header">
            <h2>Настройки профиля</h2>
            <button @click="showSettings = false" class="modal-close">×</button>
          </div>
          <form @submit.prevent="handleSave" class="modal-body">
            <div class="form-group">
              <label>Имя пользователя</label>
              <input
                v-model="profileData.username"
                type="text"
                class="form-control"
                disabled
              />
              <small class="form-hint">Имя пользователя нельзя изменить</small>
            </div>

            <div class="form-group">
              <label>Email</label>
              <input
                v-model="profileData.email"
                type="email"
                class="form-control"
                placeholder="example@mail.com"
              />
            </div>

            <div class="form-group">
              <label>Новый пароль</label>
              <input
                v-model="profileData.password"
                type="password"
                class="form-control"
                placeholder="Оставьте пустым, если не хотите менять"
                minlength="6"
              />
            </div>

            <div class="form-group">
              <label>Подтвердите новый пароль</label>
              <input
                v-model="profileData.password_confirm"
                type="password"
                class="form-control"
                placeholder="Повторите новый пароль"
              />
            </div>

            <div v-if="successMessage" class="alert alert-success">
              {{ successMessage }}
            </div>

            <div v-if="errorMessage" class="alert alert-danger">
              {{ errorMessage }}
            </div>

            <div class="modal-actions">
              <button type="button" @click="showSettings = false" class="btn-secondary">Отмена</button>
              <button type="submit" class="btn-primary" :disabled="isLoading">
                <span v-if="isLoading" class="spinner spinner-sm"></span>
                {{ isLoading ? 'Сохранение...' : 'Сохранить' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { authService, projectService } from '../services/api';

export default {
  name: 'Profile',
  data() {
    return {
      currentUser: null,
      profileData: {
        username: '',
        email: '',
        password: '',
        password_confirm: ''
      },
      projects: [],
      stats: {
        projects: 0,
        tasks: 0
      },
      loading: false,
      isLoading: false,
      successMessage: '',
      errorMessage: '',
      showSettings: false
    }
  },
  computed: {
    userInitials() {
      if (!this.currentUser?.username) return '?';
      const name = this.currentUser.username;
      return name.substring(0, 2).toUpperCase();
    }
  },
  mounted() {
    this.loadProfile();
    this.loadStats();
    this.loadProjects();
  },
  methods: {
    loadProfile() {
      this.currentUser = authService.getCurrentUser();
      console.log('🔍 Current user from storage:', this.currentUser);

      if (this.currentUser) {
        this.profileData.username = this.currentUser.username || '';
        this.profileData.email = this.currentUser.email || '';

        console.log('📧 Email:', this.profileData.email);
        console.log('👤 Username:', this.profileData.username);
      }
    },

    async loadStats() {
      try {
        const stats = await authService.getUserStats();
        this.stats = stats;
      } catch (error) {
        console.error('Error loading stats:', error);
        this.stats = { projects: 0, tasks: 0 };
      }
    },

    async loadProjects() {
      this.loading = true;
      try {
        const projects = await projectService.getProjects();
        this.projects = projects;
      } catch (error) {
        console.error('Error loading projects:', error);
        this.projects = [];
      } finally {
        this.loading = false;
      }
    },

    getProjectInitials(name) {
      if (!name) return '?';
      const words = name.split(' ');
      if (words.length >= 2) {
        return (words[0][0] + words[1][0]).toUpperCase();
      }
      return name.substring(0, 2).toUpperCase();
    },

    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      });
    },

    openProject(projectId) {
      this.$emit('openProject', projectId);
    },

    createNewProject() {
      this.$emit('createProject');
    },

    async handleSave() {
      if (this.profileData.password && this.profileData.password !== this.profileData.password_confirm) {
        this.errorMessage = 'Пароли не совпадают';
        this.successMessage = '';
        return;
      }

      if (this.profileData.password && this.profileData.password.length < 6) {
        this.errorMessage = 'Пароль должен быть минимум 6 символов';
        this.successMessage = '';
        return;
      }

      this.isLoading = true;
      this.errorMessage = '';
      this.successMessage = '';

      try {
        await authService.updateProfile({
          email: this.profileData.email,
          password: this.profileData.password || undefined
        });

        const updatedUser = authService.getCurrentUser();
        if (updatedUser) {
          updatedUser.email = this.profileData.email;
          localStorage.setItem('user', JSON.stringify(updatedUser));
          this.currentUser = updatedUser;
        }

        this.successMessage = 'Данные успешно обновлены';

        this.profileData.password = '';
        this.profileData.password_confirm = '';

        setTimeout(() => {
          this.successMessage = '';
          this.showSettings = false;
        }, 2000);

      } catch (error) {
        console.error('Update error:', error);
        if (error.response?.data) {
          const errors = error.response.data;
          if (errors.email) {
            this.errorMessage = errors.email[0];
          } else if (errors.password) {
            this.errorMessage = errors.password[0];
          } else if (errors.detail) {
            this.errorMessage = errors.detail;
          } else {
            this.errorMessage = 'Ошибка обновления данных';
          }
        } else {
          this.errorMessage = 'Ошибка обновления данных. Попробуйте позже.';
        }
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>

<style scoped>
.profile-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* Боковая панель */
.sidebar {
  width: 280px;
  background: #292961;
  color: white;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-user {
  padding: 32px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.user-avatar {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
}

.user-details h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: white;
}

.user-details p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 0;
  overflow-y: auto;
}

.nav-section {
  margin-bottom: 24px;
}

.nav-section-title {
  padding: 8px 24px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(255, 255, 255, 0.5);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 24px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border-left: 3px solid #667eea;
}

.nav-item svg {
  flex-shrink: 0;
}

.sidebar-stats {
  padding: 16px;
  display: flex;
  gap: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-box {
  flex: 1;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

/* Основной контент */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f7f8fa;
  overflow: hidden;
}

.content-header {
  background: white;
  padding: 20px 32px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #333;
}

.btn-new-project {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-new-project:hover {
  background: #357abd;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
}

/* Список проектов */
.projects-list {
  padding: 32px;
  overflow-y: auto;
  flex: 1;
}

.project-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.project-card:hover {
  border-color: #4a90e2;
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.15);
  transform: translateX(4px);
}

.project-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.project-info {
  flex: 1;
  min-width: 0;
}

.project-name {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.project-description {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.project-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #999;
}

.project-arrow {
  color: #ccc;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.project-card:hover .project-arrow {
  color: #4a90e2;
  transform: translateX(4px);
}

/* Состояния */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e0e0e0;
  border-top-color: #4a90e2;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 16px 0 8px 0;
  color: #333;
}

.empty-state p {
  font-size: 14px;
  color: #666;
  margin: 0 0 24px 0;
}

/* Модальное окно */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: #333;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
}

.form-group .form-control {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.form-group .form-control:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.form-group .form-control:disabled {
  background: #f5f5f5;
  color: #999;
}

.form-hint {
  display: block;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.alert {
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 14px;
}

.alert-success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-danger {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-primary {
  background: #4a90e2;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #357abd;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e0e0e0;
  color: #333;
}

.btn-secondary:hover {
  background: #d0d0d0;
}

.spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}
</style>
