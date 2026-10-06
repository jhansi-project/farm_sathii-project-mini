/**
 * Weather & Location Services TypeScript interfaces (Phase 8).
 * Pure front-end domain contracts matching backend schemas.
 */

export interface CurrentWeatherCondition {
  temperature_celsius: number;
  relative_humidity_percent: number;
  precipitation_mm: number;
  weather_code: number;
  condition_text: string;
  condition_icon: string;
  wind_speed_kmh?: number | null;
  observation_time: string;
}

export interface DailyForecastItem {
  date: string;
  temperature_max_celsius: number;
  temperature_min_celsius: number;
  precipitation_sum_mm: number;
  weather_code: number;
  condition_text: string;
  condition_icon: string;
}

export interface LocationInfo {
  latitude: number;
  longitude: number;
  name?: string | null;
  state?: string | null;
  country?: string | null;
}

export interface WeatherResponse {
  location: LocationInfo;
  current?: CurrentWeatherCondition | null;
  forecast?: DailyForecastItem[] | null;
  is_cached: boolean;
  cached_at?: string | null;
  expires_at?: string | null;
  provider_name: string;
  status: 'success' | 'stale_cached' | 'provider_unavailable' | 'error';
  error_message?: string | null;
}

export interface GeocodingResultItem {
  name: string;
  latitude: number;
  longitude: number;
  state?: string | null;
  country?: string | null;
  country_code?: string | null;
}
