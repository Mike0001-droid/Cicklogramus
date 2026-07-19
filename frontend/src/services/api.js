import axios from 'axios';

// Создаём axios инстанс
const api = axios.create({
  baseURL: '/api'
});

// Функция для установки токена в заголовки
export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
}

// Проверяем наличие токена при загрузке
const accessToken = localStorage.getItem('access_token');
if (accessToken) {
  setAuthToken(accessToken);
}

// Интерцептор для автоматического обновления токена
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Если ошибка 401 и запрос не был повтором
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post('/api/auth/token/refresh/', {
            refresh: refreshToken
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);
          setAuthToken(access);

          // Повторяем оригинальный запрос с новым токеном
          originalRequest.headers['Authorization'] = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Если не удалось обновить токен, очищаем хранилище
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        delete api.defaults.headers.common['Authorization'];

        // Перенаправляем на страницу входа
        if (window.location.pathname !== '/') {
          window.location.href = '/';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export const projectService = {
  async getProjects() {
    const response = await api.get('/projects/');
    return response.data;
  },

  async getProject(projectId) {
    const response = await api.get(`/projects/${projectId}/`);
    return response.data;
  },

  async getProjectTasks(projectId) {
    const response = await api.get(`/projects/${projectId}/tasks/`);
    return response.data;
  },

  async createProject(projectData) {
    const response = await api.post('/projects/', projectData);
    return response.data;
  }
};

export const workerService = {
  async getWorkers() {
    const response = await api.get('/workers/');
    return response.data;
  },

  async createWorker(workerData) {
    const response = await api.post('/workers/', workerData);
    return response.data;
  },

  async updateWorker(workerId, workerData) {
    const response = await api.put(`/workers/${workerId}/`, workerData);
    return response.data;
  }
};

export const taskService = {
  async getTasks() {
    const response = await api.get('/tasks/');
    return response.data;
  },

  async createTask(taskData) {
    const response = await api.post('/tasks/', taskData);
    return response.data;
  },

  async updateTask(taskId, taskData) {
    const response = await api.put(`/tasks/${taskId}/`, taskData);
    return response.data;
  },

  async deleteTask(taskId) {
    const response = await api.delete(`/tasks/${taskId}/`);
    return response.data;
  },

  async bulkUpdate(tasksData, projectId) {
    const response = await api.post('/tasks/bulk_update/', {
      tasks: tasksData,
      project_id: projectId
    });
    return response.data;
  },

  async reorderTasks(taskIds, projectId) {
    const response = await api.post('/tasks/reorder_tasks/', {
      task_ids: taskIds,
      project_id: projectId
    });
    return response.data;
  }
};

export const operationBlockService = {
  async createBlock(blockData) {
    const response = await api.post('/operation-blocks/', blockData);
    return response.data;
  }
};

// Сервис аутентификации
export const authService = {
  async login(username, password) {
    const response = await axios.post('/api/auth/token/', {
      username,
      password
    });

    const { access, refresh, user } = response.data;

    return {
      access,
      refresh,
      user
    };
  },

  async register(username, password, email = '') {
    const response = await axios.post('/api/auth/register/', {
      username,
      password,
      email
    });

    // После успешной регистрации сразу выполняем вход
    return this.login(username, password);
  },

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    delete api.defaults.headers.common['Authorization'];
  },

  decodeToken(token) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));

      return JSON.parse(jsonPayload);
    } catch (e) {
      console.error('Error decoding token:', e);
      return null;
    }
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    console.log('📖 Reading user from localStorage:', userStr);

    if (userStr && userStr !== 'undefined' && userStr !== 'null') {
      try {
        const user = JSON.parse(userStr);
        console.log('✅ Parsed user:', user);
        return user;
      } catch (e) {
        console.error('❌ Error parsing user:', e);
        // Очищаем некорректные данные
        localStorage.removeItem('user');
        return null;
      }
    }
    console.log('❌ No valid user found in localStorage');
    return null;
  },

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },

  async getUserStats() {
    try {
      const response = await api.get('/auth/user/stats/');
      return response.data;
    } catch (error) {
      console.error('Error fetching user stats:', error);
      return { projects: 0, tasks: 0 };
    }
  },

  async updateProfile(data) {
    const response = await api.put('/auth/user/profile/', data);
    return response.data;
  }
};

export default api;
