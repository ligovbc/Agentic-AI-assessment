import axios from 'axios';
import type { AgenticRequest, AgenticResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const agenticAPI = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/');
    return response.data;
  },

  // Submit completion request (JSON)
  submitCompletion: async (request: AgenticRequest): Promise<AgenticResponse> => {
    const response = await api.post<AgenticResponse>('/v1/completions', request);
    return response.data;
  },

  // Submit completion with PDF
  submitCompletionWithPDF: async (
    request: AgenticRequest,
    pdfFile: File
  ): Promise<AgenticResponse> => {
    const formData = new FormData();
    formData.append('pdf_file', pdfFile);
    formData.append('prompt', request.prompt);
    if (request.system_prompt) {
      formData.append('system_prompt', request.system_prompt);
    }
    formData.append('num_self_consistency', request.num_self_consistency.toString());
    formData.append('num_cot', request.num_cot.toString());
    formData.append('model', request.model);
    formData.append('temperature', request.temperature.toString());

    const response = await api.post<AgenticResponse>('/v1/completions', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export default api;
