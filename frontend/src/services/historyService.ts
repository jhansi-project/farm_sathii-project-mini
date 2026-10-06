import { apiClient } from './api';
import { StandardApiResponse } from '../types/auth';
import {
  UserHistorySummary,
  PaginatedCropHistory,
  PaginatedDiseaseHistory,
  PaginatedAdvisoryHistory,
} from '../types/history';
import { CropRecommendationHistoryItem } from '../types/crop';
import { DiseaseHistoryItem } from '../types/disease';
import { AdvisoryConversationDetail } from '../types/advisory';

export const historyService = {
  async getSummary(limit: number = 10): Promise<UserHistorySummary> {
    const res = await apiClient.get<StandardApiResponse<UserHistorySummary>>(
      `/history?limit=${limit}`
    );
    return res.data.data;
  },

  async getCropHistory(skip: number = 0, limit: number = 20): Promise<PaginatedCropHistory> {
    const res = await apiClient.get<StandardApiResponse<PaginatedCropHistory>>(
      `/history/crop-recommendations?skip=${skip}&limit=${limit}`
    );
    return res.data.data;
  },

  async getCropDetail(id: string): Promise<CropRecommendationHistoryItem> {
    const res = await apiClient.get<StandardApiResponse<CropRecommendationHistoryItem>>(
      `/history/crop-recommendations/${id}`
    );
    return res.data.data;
  },

  async getDiseaseHistory(skip: number = 0, limit: number = 20): Promise<PaginatedDiseaseHistory> {
    const res = await apiClient.get<StandardApiResponse<PaginatedDiseaseHistory>>(
      `/history/disease-diagnoses?skip=${skip}&limit=${limit}`
    );
    return res.data.data;
  },

  async getDiseaseDetail(id: string): Promise<DiseaseHistoryItem> {
    const res = await apiClient.get<StandardApiResponse<DiseaseHistoryItem>>(
      `/history/disease-diagnoses/${id}`
    );
    return res.data.data;
  },

  async getAdvisoryHistory(skip: number = 0, limit: number = 20): Promise<PaginatedAdvisoryHistory> {
    const res = await apiClient.get<StandardApiResponse<PaginatedAdvisoryHistory>>(
      `/history/advisory-conversations?skip=${skip}&limit=${limit}`
    );
    return res.data.data;
  },

  async getAdvisoryDetail(id: string): Promise<AdvisoryConversationDetail> {
    const res = await apiClient.get<StandardApiResponse<AdvisoryConversationDetail>>(
      `/history/advisory-conversations/${id}`
    );
    return res.data.data;
  },
};
