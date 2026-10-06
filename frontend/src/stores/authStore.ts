import { create } from 'zustand';
import { FarmerProfile, TokenResponse, UserWithProfile } from '../types/auth';

interface AuthState {
  user: UserWithProfile | null;
  accessToken: string | null;
  refreshToken: string | null;
  language: string;
  isAuthenticated: boolean;
  setAuth: (tokenData: TokenResponse) => void;
  setUser: (user: UserWithProfile) => void;
  setProfile: (profile: FarmerProfile) => void;
  setLanguage: (lang: string) => void;
  logout: () => void;
}

const getSavedUser = (): UserWithProfile | null => {
  try {
    const raw = localStorage.getItem('farmsathi_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const useAuthStore = create<AuthState>((set) => ({
  user: getSavedUser(),
  accessToken: localStorage.getItem('farmsathi_access_token'),
  refreshToken: localStorage.getItem('farmsathi_refresh_token'),
  language: localStorage.getItem('farmsathi_lang') || 'en',
  isAuthenticated: Boolean(localStorage.getItem('farmsathi_access_token')),

  setAuth: (tokenData: TokenResponse) => {
    localStorage.setItem('farmsathi_access_token', tokenData.access_token);
    localStorage.setItem('farmsathi_refresh_token', tokenData.refresh_token);
    localStorage.setItem('farmsathi_user', JSON.stringify(tokenData.user));
    if (tokenData.user.profile?.preferred_language) {
      localStorage.setItem('farmsathi_lang', tokenData.user.profile.preferred_language);
    }
    set({
      user: tokenData.user,
      accessToken: tokenData.access_token,
      refreshToken: tokenData.refresh_token,
      language: tokenData.user.profile?.preferred_language || 'en',
      isAuthenticated: true,
    });
  },

  setUser: (user: UserWithProfile) => {
    localStorage.setItem('farmsathi_user', JSON.stringify(user));
    set({ user });
  },

  setProfile: (profile: FarmerProfile) => {
    set((state) => {
      if (!state.user) return state;
      const updatedUser: UserWithProfile = { ...state.user, profile };
      localStorage.setItem('farmsathi_user', JSON.stringify(updatedUser));
      return { user: updatedUser };
    });
  },

  setLanguage: (lang: string) => {
    localStorage.setItem('farmsathi_lang', lang);
    set({ language: lang });
  },

  logout: () => {
    localStorage.removeItem('farmsathi_access_token');
    localStorage.removeItem('farmsathi_refresh_token');
    localStorage.removeItem('farmsathi_user');
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    });
  },
}));
