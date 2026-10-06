import { apiClient } from './api';
import { StandardApiResponse } from '../types/auth';
import {
  CropRecommendationPayload,
  CropRecommendationResult,
  CropRecommendationHistoryItem,
} from '../types/crop';

export const cropService = {
  async getRecommendation(
    payload: CropRecommendationPayload
  ): Promise<CropRecommendationResult> {
    const res = await apiClient.post<StandardApiResponse<CropRecommendationResult>>(
      '/crops/recommend',
      payload
    );
    return res.data.data;
  },

  async getHistory(): Promise<CropRecommendationHistoryItem[]> {
    const res = await apiClient.get<StandardApiResponse<CropRecommendationHistoryItem[]>>(
      '/crops/history'
    );
    return res.data.data;
  },
};
