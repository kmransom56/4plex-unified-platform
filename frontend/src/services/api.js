import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health checks
export const getHealthStatus = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getDiscoveryHealth = async () => {
  const response = await api.get('/health/discovery');
  return response.data;
};

export const getValuationHealth = async () => {
  const response = await api.get('/health/valuation');
  return response.data;
};

// Discovery endpoints
export const startDiscovery = async (discoveryRequest) => {
  const response = await api.post('/api/discovery/start', discoveryRequest);
  return response.data;
};

export const getDiscoveryStatus = async (jobId) => {
  const response = await api.get(`/api/discovery/status/${jobId}`);
  return response.data;
};

export const getDiscoveryResults = async (jobId) => {
  const response = await api.get(`/api/discovery/results/${jobId}`);
  return response.data;
};

// Property endpoints
export const getProperties = async (params = {}) => {
  const response = await api.get('/api/properties', { params });
  return response.data;
};

export const getPropertyDetails = async (propertyId) => {
  const response = await api.get(`/api/properties/${propertyId}`);
  return response.data;
};

export const queuePropertyAnalysis = async (propertyId, priority = 'normal') => {
  const response = await api.post(`/api/properties/${propertyId}/analyze`, null, {
    params: { priority }
  });
  return response.data;
};

// Valuation endpoints
export const analyzeProperty = async (analysisRequest) => {
  const response = await api.post('/api/valuation/analyze', analysisRequest);
  return response.data;
};

export const getAnalysisStatus = async (jobId) => {
  const response = await api.get(`/api/valuation/status/${jobId}`);
  return response.data;
};

export const getAnalysisResults = async (jobId) => {
  const response = await api.get(`/api/valuation/results/${jobId}`);
  return response.data;
};

// Investment opportunities
export const getInvestmentOpportunities = async (params = {}) => {
  const response = await api.get('/api/opportunities', { params });
  return response.data;
};

export const getOpportunityAlerts = async () => {
  const response = await api.get('/api/opportunities/alerts');
  return response.data;
};

// Analytics endpoints
export const getDashboardAnalytics = async () => {
  const response = await api.get('/api/analytics/dashboard');
  return response.data;
};

export const getPerformanceMetrics = async () => {
  const response = await api.get('/api/analytics/performance');
  return response.data;
};

export const getCountyAnalytics = async () => {
  const response = await api.get('/api/analytics/counties');
  return response.data;
};

// System endpoints
export const triggerDataSync = async () => {
  const response = await api.post('/api/system/sync');
  return response.data;
};

export const getSystemMetrics = async () => {
  const response = await api.get('/api/system/metrics');
  return response.data;
};

export default api;
