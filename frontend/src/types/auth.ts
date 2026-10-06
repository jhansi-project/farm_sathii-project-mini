export interface FarmerProfile {
  id: string;
  user_id: string;
  preferred_language: string;
  state?: string | null;
  district?: string | null;
  village?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  land_size_acres?: number | null;
  soil_type?: string | null;
  irrigation_source?: string | null;
  updated_at: string;
}

export interface User {
  id: string;
  full_name: string;
  phone?: string | null;
  email?: string | null;
  is_active: boolean;
  created_at: string;
}

export interface UserWithProfile extends User {
  profile?: FarmerProfile | null;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: UserWithProfile;
}

export interface StandardApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
  errors?: Record<string, any> | null;
  timestamp: string;
}
