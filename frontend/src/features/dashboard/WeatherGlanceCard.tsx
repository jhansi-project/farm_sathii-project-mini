import React from 'react';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { CloudSun, Droplets, Wind, MapPin, RefreshCw } from 'lucide-react';

interface WeatherGlanceCardProps {
  locationName?: string;
  temperature?: number;
  humidity?: number;
  precipitation?: number;
  conditionText?: string;
  onRequestLocation: () => void;
  isLoading?: boolean;
}

export const WeatherGlanceCard: React.FC<WeatherGlanceCardProps> = ({
  locationName = 'Local Weather',
  temperature = 27.5,
  humidity = 68,
  precipitation = 0.0,
  conditionText = 'Partly Cloudy',
  onRequestLocation,
  isLoading = false,
}) => {
  return (
    <Card
      style={{
        background: 'var(--color-weather-bg, #354024)',
        color: 'var(--color-weather-text, #E5D7C4)',
        border: 'none',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Decorative ambient backdrop */}
      <div
        style={{
          position: 'absolute',
          right: '-10px',
          bottom: '-15px',
          opacity: 0.15,
          pointerEvents: 'none',
        }}
      >
        <CloudSun size={140} color="#E5D7C4" />
      </div>

      <div style={{ position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: 'var(--font-size-sm)', opacity: 0.9 }}>
            <MapPin size={16} />
            <span>{locationName}</span>
          </div>
          <Badge
            variant="neutral"
            size="sm"
            style={{
              backgroundColor: 'var(--color-surface, #E5D7C4)',
              color: 'var(--color-icon-primary, #354024)',
              cursor: 'pointer',
            }}
            onClick={onRequestLocation}
          >
            <RefreshCw size={12} style={{ animation: isLoading ? 'farmsathi-spin 1s linear infinite' : 'none' }} />
            <span>Detect Location</span>
          </Badge>
        </div>

        <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '0.35rem' }}>
          <span style={{ fontSize: '2.5rem', fontWeight: 800, lineHeight: 1 }}>
            {temperature.toFixed(1)}°
          </span>
          <span style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600 }}>C</span>
          <span style={{ marginLeft: '0.5rem', fontSize: 'var(--font-size-base)', opacity: 0.9 }}>
            {conditionText}
          </span>
        </div>

        <div
          style={{
            display: 'flex',
            gap: '1.25rem',
            marginTop: '1rem',
            paddingTop: '0.75rem',
            borderTop: '1px solid var(--color-border, #CFBB99)',
            fontSize: 'var(--font-size-xs)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Droplets size={14} />
            <span>Humidity: {humidity}%</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Wind size={14} />
            <span>Precipitation: {precipitation} mm</span>
          </div>
        </div>
      </div>
    </Card>
  );
};
