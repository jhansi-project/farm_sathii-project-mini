import { create } from 'zustand';
import { weatherService } from '../services/weatherService';

export interface LocationState {
  latitude: number | null;
  longitude: number | null;
  locationName: string | null;
  stateName: string | null;
  source: 'gps' | 'manual' | 'profile' | 'none';
  loading: boolean;
  error: string | null;

  detectGpsLocation: () => Promise<boolean>;
  setManualLocation: (name: string, lat: number, lon: number, state?: string | null) => void;
  clearLocation: () => void;
  getDisplayLabel: () => string;
}

const STORAGE_KEY = 'farmsathi_active_location';

const loadSavedLocation = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      return JSON.parse(raw);
    }
  } catch {
    // Ignore parse error
  }
  return null;
};

const saved = loadSavedLocation();

export const useLocationStore = create<LocationState>((set, get) => ({
  latitude: saved?.latitude ?? null,
  longitude: saved?.longitude ?? null,
  locationName: saved?.locationName ?? null,
  stateName: saved?.stateName ?? null,
  source: saved?.source ?? 'none',
  loading: false,
  error: null,

  detectGpsLocation: async (): Promise<boolean> => {
    if (!navigator.geolocation) {
      set({ error: 'Geolocation is not supported by your browser.', loading: false });
      return false;
    }

    set({ loading: true, error: null });

    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const lat = position.coords.latitude;
          const lon = position.coords.longitude;

          try {
            const geocodeResult = await weatherService.reverseGeocode(lat, lon);
            const cityName = geocodeResult.name || 'Local Farm';
            const state = geocodeResult.state || '';
            const formatted = state && cityName !== state ? `${cityName}, ${state}` : cityName;

            const locData = {
              latitude: lat,
              longitude: lon,
              locationName: formatted,
              stateName: state,
              source: 'gps' as const,
              loading: false,
              error: null,
            };

            localStorage.setItem(STORAGE_KEY, JSON.stringify(locData));
            set(locData);
            resolve(true);
          } catch {
            set({
              latitude: lat,
              longitude: lon,
              locationName: null,
              stateName: null,
              source: 'none',
              loading: false,
              error: 'reverse_geocoding_failed',
            });
            resolve(false);
          }
        },
        (err) => {
          set({
            loading: false,
            error: err.code === err.PERMISSION_DENIED ? 'permission_denied' : 'detection_failed',
          });
          resolve(false);
        },
        { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 }
      );
    });
  },

  setManualLocation: (name: string, lat: number, lon: number, state?: string | null) => {
    const formatted = state && !name.includes(state) ? `${name}, ${state}` : name;
    const locData = {
      latitude: lat,
      longitude: lon,
      locationName: formatted,
      stateName: state || null,
      source: 'manual' as const,
      loading: false,
      error: null,
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(locData));
    set(locData);
  },

  clearLocation: () => {
    localStorage.removeItem(STORAGE_KEY);
    set({
      latitude: null,
      longitude: null,
      locationName: null,
      stateName: null,
      source: 'none',
      loading: false,
      error: null,
    });
  },

  getDisplayLabel: () => {
    const { locationName } = get();
    if (locationName) return locationName;
    return 'Select Location';
  },
}));
