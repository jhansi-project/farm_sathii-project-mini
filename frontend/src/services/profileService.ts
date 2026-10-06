import { apiClient } from './api';
import { FarmerProfile, StandardApiResponse } from '../types/auth';

export interface UpdateProfilePayload {
  preferred_language?: string;
  state?: string;
  district?: string;
  village?: string;
  latitude?: number;
  longitude?: number;
  land_size_acres?: number;
  soil_type?: string;
  irrigation_source?: string;
}

export const profileService = {
  async getProfile(): Promise<FarmerProfile> {
    const res = await apiClient.get<StandardApiResponse<FarmerProfile>>('/profile');
    return res.data.data;
  },

  async updateProfile(payload: UpdateProfilePayload): Promise<FarmerProfile> {
    const res = await apiClient.put<StandardApiResponse<FarmerProfile>>('/profile', payload);
    return res.data.data;
  },
};
