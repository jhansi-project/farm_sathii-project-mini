import { create } from 'zustand';
import { useAuthStore } from './authStore';

export interface SupportedLanguage {
  code: string;
  name: string;
  nativeName: string;
}

export const SUPPORTED_LANGUAGES: SupportedLanguage[] = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी' },
];

interface LanguageState {
  currentLanguage: string;
  hasCompletedWelcome: boolean;
  setLanguage: (code: string) => void;
  completeWelcome: () => void;
}

const getInitialLang = (): string => {
  const lang = localStorage.getItem('farmsathi_lang') || 'en';
  if (typeof document !== 'undefined') {
    document.documentElement.lang = lang;
    document.documentElement.setAttribute('data-lang', lang);
  }
  return lang;
};

const getInitialWelcomeStatus = (): boolean => {
  return localStorage.getItem('farmsathi_welcome_completed') === 'true';
};

export const useLanguageStore = create<LanguageState>((set) => ({
  currentLanguage: getInitialLang(),
  hasCompletedWelcome: getInitialWelcomeStatus(),

  setLanguage: (code: string) => {
    localStorage.setItem('farmsathi_lang', code);
    useAuthStore.getState().setLanguage(code);
    if (typeof document !== 'undefined') {
      document.documentElement.lang = code;
      document.documentElement.setAttribute('data-lang', code);
    }
    set({ currentLanguage: code });
  },

  completeWelcome: () => {
    localStorage.setItem('farmsathi_welcome_completed', 'true');
    set({ hasCompletedWelcome: true });
  },
}));
