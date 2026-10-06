/**
 * Weather & Location API client service (Phase 8).
 * Communicates strictly with backend endpoints, never calling third-party APIs directly.
 */

import { apiClient } from './api';
import { WeatherResponse, GeocodingResultItem } from '../types/weather';

interface StandardResponse<T> {
  success: boolean;
  data: T;
  message: string;
  errors?: Record<string, unknown> | null;
  timestamp: string;
}

export const weatherService = {
  /**
   * Fetch current weather conditions for geographic coordinates.
   */
  async getCurrentWeather(
    latitude: number,
    longitude: number,
    locationName?: string
  ): Promise<WeatherResponse> {
    const params: Record<string, unknown> = { latitude, longitude };
    if (locationName) params.location_name = locationName;

    const response = await apiClient.get<StandardResponse<WeatherResponse>>('/weather/current', {
      params,
    });
    return response.data.data;
  },

  /**
   * Fetch multi-day forecast for geographic coordinates.
   */
  async getForecast(
    latitude: number,
    longitude: number,
    days: number = 7,
    locationName?: string
  ): Promise<WeatherResponse> {
    const params: Record<string, unknown> = { latitude, longitude, days };
    if (locationName) params.location_name = locationName;

    const response = await apiClient.get<StandardResponse<WeatherResponse>>('/weather/forecast', {
      params,
    });
    return response.data.data;
  },

  /**
   * Fetch weather based on the authenticated farmer's saved profile location.
   */
  async getProfileWeather(): Promise<WeatherResponse> {
    const response = await apiClient.get<StandardResponse<WeatherResponse>>('/weather/profile');
    return response.data.data;
  },

  /**
   * Search locations by city / town name for manual coordinate selection.
   */
  async searchLocations(query: string, limit: number = 5): Promise<GeocodingResultItem[]> {
    if (!query || query.trim().length < 2) return [];
    const response = await apiClient.get<StandardResponse<GeocodingResultItem[]>>('/weather/search', {
      params: { query: query.trim(), limit },
    });
    return response.data.data;
  },

  /**
   * Reverse geocode GPS coordinates to human-readable city/district/state.
   */
  async reverseGeocode(latitude: number, longitude: number): Promise<GeocodingResultItem> {
    const response = await apiClient.get<StandardResponse<GeocodingResultItem>>('/weather/reverse-geocode', {
      params: { latitude, longitude },
    });
    return response.data.data;
  },
};
