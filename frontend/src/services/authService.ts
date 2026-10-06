import { apiClient } from './api';
import { StandardApiResponse, TokenResponse, UserWithProfile } from '../types/auth';

export interface RegisterPayload {
  full_name: string;
  phone?: string;
  email?: string;
  password: string;
  preferred_language?: string;
}

export interface LoginPayload {
  identifier: string;
  password: string;
}

export const authService = {
  async register(payload: RegisterPayload): Promise<TokenResponse> {
    const res = await apiClient.post<StandardApiResponse<TokenResponse>>('/auth/register', payload);
    return res.data.data;
  },

  async login(payload: LoginPayload): Promise<TokenResponse> {
    const res = await apiClient.post<StandardApiResponse<TokenResponse>>('/auth/login', payload);
    return res.data.data;
  },

  async getMe(): Promise<UserWithProfile> {
    const res = await apiClient.get<StandardApiResponse<UserWithProfile>>('/auth/me');
    return res.data.data;
  },

  async refreshToken(refreshToken: string): Promise<string> {
    const res = await apiClient.post<StandardApiResponse<{ access_token: string }>>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return res.data.data.access_token;
  },
};
