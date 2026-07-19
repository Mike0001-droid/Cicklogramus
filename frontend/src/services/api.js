import axios from 'axios';

// Создаём axios инстанс
const api = axios.create({
  baseURL: '/api'
});

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

export default api;
