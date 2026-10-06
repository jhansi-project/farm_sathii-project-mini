import { apiClient } from './api';
import { StandardApiResponse } from '../types/auth';
import { DiseaseDiagnosisResult, DiseaseHistoryItem } from '../types/disease';

export const diseaseService = {
  async diagnoseImage(file: File): Promise<DiseaseDiagnosisResult> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await apiClient.post<StandardApiResponse<DiseaseDiagnosisResult>>(
      '/diseases/diagnose',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return res.data.data;
  },

  async getHistory(): Promise<DiseaseHistoryItem[]> {
    const res = await apiClient.get<StandardApiResponse<DiseaseHistoryItem[]>>(
      '/diseases/history'
    );
    return res.data.data;
  },
};
