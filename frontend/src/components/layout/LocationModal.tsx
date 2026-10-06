import React, { useState } from 'react';
import { useLocationStore } from '../../stores/locationStore';
import { useTranslation } from '../../i18n/useTranslation';
import { weatherService } from '../../services/weatherService';
import { GeocodingResultItem } from '../../types/weather';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';

interface LocationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const LocationModal: React.FC<LocationModalProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const {
    locationName,
    loading: detectingGps,
    error,
    detectGpsLocation,
    setManualLocation,
  } = useLocationStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<GeocodingResultItem[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleGpsDetect = async () => {
    const success = await detectGpsLocation();
    if (success) {
      onClose();
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = searchQuery.trim();
    if (q.length < 2) return;

    setSearching(true);
    setSearchError(null);
    try {
      const results = await weatherService.searchLocations(q, 8);
      setSearchResults(results);
      if (results.length === 0) {
        setSearchError(t.common.locationNotFound || 'No locations found matching your query.');
      }
    } catch {
      setSearchError('Unable to search locations right now. Please check your connection.');
    } finally {
      setSearching(false);
    }
  };

  const handleSelectResult = (item: GeocodingResultItem) => {
    setManualLocation(item.name, item.latitude, item.longitude, item.state);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t.common.searchLocation || 'Select Farm Location'}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* Active Location Display */}
        {locationName && (
          <div
            style={{
              backgroundColor: 'var(--color-primary-light)',
              borderRadius: 'var(--radius-lg)',
              padding: '0.85rem 1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              border: '1px solid var(--color-primary-subtle)',
            }}
          >
            <div>
              <span
                style={{
                  fontSize: '11px',
                  color: 'var(--color-primary)',
                  fontWeight: 700,
                  display: 'block',
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                }}
              >
                Current Active Location
              </span>
              <span
                style={{
                  fontSize: 'var(--font-size-sm)',
                  fontWeight: 700,
                  color: 'var(--color-text-primary)',
                }}
              >
                📍 {locationName}
              </span>
            </div>
            <span
              style={{
                fontSize: '11px',
                fontWeight: 600,
                color: 'var(--color-primary)',
                backgroundColor: 'var(--color-surface)',
                padding: '0.2rem 0.6rem',
                borderRadius: 'var(--radius-full)',
                boxShadow: 'var(--shadow-xs)',
              }}
            >
              Active
            </span>
          </div>
        )}

        {/* GPS Auto-Detect Button */}
        <div>
          <Button
            type="button"
            variant="outline"
            fullWidth
            onClick={handleGpsDetect}
            isLoading={detectingGps}
            leftIcon={
              <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
                my_location
              </span>
            }
          >
            {t.nav.detectLocation || 'Detect GPS Location Automatically'}
          </Button>
          {error && (
            <p
              style={{
                fontSize: 'var(--font-size-xs)',
                color: 'var(--color-error)',
                marginTop: '0.4rem',
                lineHeight: 1.4,
              }}
            >
              {error}
            </p>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--color-border-subtle)' }} />
          <span
            style={{
              fontSize: 'var(--font-size-xs)',
              color: 'var(--color-text-muted)',
              fontWeight: 600,
              textTransform: 'uppercase',
            }}
          >
            Or Search Manually
          </span>
          <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--color-border-subtle)' }} />
        </div>

        {/* Manual Search Form */}
        <form onSubmit={handleSearch} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <Input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="e.g. Warangal, Ludhiana, Pune..."
              leftIcon={
                <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
                  search
                </span>
              }
            />
            <Button
              type="submit"
              isLoading={searching}
              disabled={searchQuery.trim().length < 2}
              style={{ flexShrink: 0 }}
            >
              Search
            </Button>
          </div>
        </form>

        {/* Search Results */}
        {searchError && (
          <div
            style={{
              padding: '0.75rem 1rem',
              backgroundColor: 'var(--color-warning-bg)',
              color: 'var(--color-warning)',
              border: '1px solid var(--color-warning-border)',
              borderRadius: 'var(--radius-md)',
              fontSize: 'var(--font-size-xs)',
              fontWeight: 500,
            }}
          >
            {searchError}
          </div>
        )}

        {searchResults.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '220px', overflowY: 'auto' }}>
            {searchResults.map((item, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectResult(item)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.65rem 0.85rem',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--color-surface-container-low)',
                  border: '1px solid var(--color-border)',
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-primary-light)';
                  e.currentTarget.style.borderColor = 'var(--color-primary-subtle)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-surface-container-low)';
                  e.currentTarget.style.borderColor = 'var(--color-border)';
                }}
              >
                <div>
                  <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                    {item.name}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)' }}>
                    {[item.state, item.country].filter(Boolean).join(', ')}
                  </div>
                </div>
                <span className="material-symbols-outlined" style={{ fontSize: '18px', color: 'var(--color-primary)' }}>
                  chevron_right
                </span>
              </button>
            ))}
          </div>
        )}
      </div>
    </Modal>
  );
};
