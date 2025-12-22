import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const amendmentAPI = {
  getAll: (params = {}) => {
    return apiClient.get('/amendments', { params });
  },

  getById: (id) => {
    return apiClient.get(`/amendments/${id}`);
  },

  getByReference: (reference) => {
    return apiClient.get(`/amendments/reference/${reference}`);
  },

  create: (data) => {
    return apiClient.post('/amendments', data);
  },

  update: (id, data) => {
    return apiClient.put(`/amendments/${id}`, data);
  },

  delete: (id) => {
    return apiClient.delete(`/amendments/${id}`);
  },

  bulkUpdate: (updates) => {
    return apiClient.post('/amendments/bulk-update', updates);
  },

  getStats: () => {
    return apiClient.get('/amendments/stats');
  },

  addProgress: (id, data) => {
    return apiClient.post(`/amendments/${id}/progress`, data);
  },

  getProgress: (id) => {
    return apiClient.get(`/amendments/${id}/progress`);
  },

  linkAmendments: (id, linkedId, linkType = 'Related') => {
    return apiClient.post(`/amendments/${id}/links`, {
      linked_amendment_id: linkedId,
      link_type: linkType,
    });
  },

  unlinkAmendments: (id, linkedId) => {
    return apiClient.delete(`/amendments/${id}/links/${linkedId}`);
  },
};

export const referenceAPI = {
  getStatuses: () => {
    return apiClient.get('/reference/statuses');
  },

  getPriorities: () => {
    return apiClient.get('/reference/priorities');
  },

  getTypes: () => {
    return apiClient.get('/reference/types');
  },

  getForces: () => {
    return apiClient.get('/reference/forces');
  },

  getDevelopmentStatuses: () => {
    return apiClient.get('/reference/development-statuses');
  },

  getLinkTypes: () => {
    return apiClient.get('/reference/link-types');
  },
};

export default apiClient;
