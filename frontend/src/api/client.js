import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getTemplates = async () => {
  const response = await apiClient.get('/api/documents/templates');
  return response.data;
};

export const generateDocument = async (docType, config, useAi = true, bomItems = [], includeBom = false, includeSow = false) => {
  const response = await apiClient.post(
    '/api/documents/generate',
    {
      doc_type: docType,
      config,
      use_ai: useAi,
      include_bom: includeBom,
      include_sow: includeSow,
      bom_items: bomItems,
    },
    { responseType: 'blob' }
  );
  
  // Create a download link for the blob
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  
  // Try to extract filename from headers, otherwise use a fallback
  let fileName = `${docType.toUpperCase()}_Document.docx`;
  const disposition = response.headers['content-disposition'];
  if (disposition && disposition.includes('filename=')) {
    fileName = disposition.split('filename=')[1].replace(/"/g, '');
  }
  
  link.setAttribute('download', fileName);
  document.body.appendChild(link);
  link.click();
  link.parentNode.removeChild(link);
  
  return true;
};

export const previewDocument = async (docType, config) => {
  const response = await apiClient.post('/api/documents/preview', {
    doc_type: docType,
    config,
  });
  return response.data;
};

export const searchEquipment = async (query, projectType = '', budgetRange = '', currency = 'MGA') => {
  const response = await apiClient.post('/api/search/equipment', {
    query,
    project_type: projectType,
    budget_range: budgetRange,
    currency,
  });
  return response.data;
};

export const searchDatasheet = async (equipmentName, brand = '', model = '') => {
  const response = await apiClient.post('/api/search/datasheet', {
    equipment_name: equipmentName,
    brand,
    model,
  });
  return response.data;
};

export const searchPrices = async (equipmentList) => {
  const response = await apiClient.post('/api/search/prices', {
    equipment_list: equipmentList,
  });
  return response.data;
};

export const analyzeRFP = async (emailContent) => {
  const response = await apiClient.post('/api/documents/analyze-rfp', {
    email_content: emailContent,
  });
  return response.data;
};

export default {
  getTemplates,
  generateDocument,
  previewDocument,
  searchEquipment,
  searchDatasheet,
  searchPrices,
  analyzeRFP,
};
