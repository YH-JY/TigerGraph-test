import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const discoverAssets = async () => {
  const response = await api.post('/api/discover');
  return response.data;
};

export const importAssets = async () => {
  const response = await api.post('/api/import');
  return response.data;
};

export const queryAttackPaths = async (params: any) => {
  const response = await api.post('/api/query/attack-paths', params);
  return response.data;
};

export const getGraphVisualization = async () => {
  const response = await api.get('/api/visualize/graph');
  return response.data;
};

export const getStatistics = async () => {
  const response = await api.get('/api/statistics');
  return response.data;
};

export const getAssetTypes = async () => {
  const response = await api.get('/api/assets/types');
  return response.data;
};

export default api;