import React, { useState, useEffect, useCallback } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { useLocationStore } from '../../stores/locationStore';
import { useTranslation } from '../../i18n/useTranslation';
import { weatherService } from '../../services/weatherService';
import { WeatherResponse } from '../../types/weather';
import { historyService } from '../../services/historyService';
import { UnifiedHistoryItem } from '../../types/history';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { EmptyState } from '../../components/ui/EmptyState';
import { Skeleton } from '../../components/ui/Skeleton';

export type AppNavTab = 'home' | 'ask' | 'crops' | 'my-crops' | 'diagnosis' | 'history' | 'profile';

interface DashboardViewProps {
  onNavigate: (tab: AppNavTab, queryContext?: string, conversationId?: string) => void;
  onOpenAuth: () => void;
  onOpenProfile: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  onNavigate,
  onOpenAuth,
}) => {
  const { user, isAuthenticated } = useAuthStore();
  const { latitude, longitude, locationName, detectGpsLocation } = useLocationStore();
  const { t } = useTranslation();

  const [askQuery, setAskQuery] = useState('');
  const [weatherData, setWeatherData] = useState<WeatherResponse | null>(null);
  const [weatherLoading, setWeatherLoading] = useState<boolean>(false);
  const [weatherError, setWeatherError] = useState<string | null>(null);

  const [recentActivities, setRecentActivities] = useState<UnifiedHistoryItem[]>([]);
  const [loadingHistory, setLoadingHistory] = useState<boolean>(false);

  const farmerName = user?.full_name || t.dashboard.greeting;

  // 1. Fetch real weather for active coordinates
  const fetchWeather = useCallback(async () => {
    if (latitude === null || longitude === null) {
      setWeatherData(null);
      return;
    }

    setWeatherLoading(true);
    setWeatherError(null);
    try {
      const data = await weatherService.getCurrentWeather(
        latitude,
        longitude,
        locationName || undefined
      );
      setWeatherData(data);
    } catch {
      setWeatherError(t.weather.unavailable);
      setWeatherData(null);
    } finally {
      setWeatherLoading(false);
    }
  }, [latitude, longitude, locationName, t.weather.unavailable]);

  useEffect(() => {
    fetchWeather();
  }, [fetchWeather]);

  // 2. Fetch real history for authenticated farmer
  useEffect(() => {
    if (!isAuthenticated || !user) {
      setRecentActivities([]);
      return;
    }

    let isMounted = true;
    const loadHistory = async () => {
      setLoadingHistory(true);
      try {
        const summary = await historyService.getSummary(4);
        if (isMounted && summary?.recent_activities) {
          setRecentActivities(summary.recent_activities);
        }
      } catch {
        if (isMounted) setRecentActivities([]);
      } finally {
        if (isMounted) setLoadingHistory(false);
      }
    };

    loadHistory();
    return () => {
      isMounted = false;
    };
  }, [isAuthenticated, user]);

  const handleAskSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!askQuery.trim()) return;
    onNavigate('ask', askQuery.trim());
  };

  const handleFormatTime = (isoStr: string) => {
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch {
      return '';
    }
  };

  return (
    <div className="farmsathi-page-container">
      {/* 1. Welcoming Hero Banner */}
      <section
        style={{
          background: 'linear-gradient(135deg, #354024 0%, #4C3D19 100%)',
          borderRadius: 'var(--radius-xl)',
          padding: '1.75rem 1.5rem',
          color: 'var(--color-text-inverse, #E5D7C4)',
          boxShadow: 'var(--shadow-sm)',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Subtle Atmospheric Rice Crop Layer (IMAGE 1: Close-up mature rice crop) */}
        <div
          aria-hidden="true"
          style={{
            position: 'absolute',
            inset: 0,
            backgroundImage: 'url(/assets/rice_crop_close.jpg)',
            backgroundPosition: 'right 25%',
            backgroundSize: 'cover',
            backgroundRepeat: 'no-repeat',
            opacity: 0.16,
            pointerEvents: 'none',
            zIndex: 1,
          }}
        />

        <div style={{ position: 'relative', zIndex: 2 }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.45rem',
              backgroundColor: 'rgba(229, 215, 196, 0.15)',
              padding: '0.25rem 0.65rem',
              borderRadius: 'var(--radius-full)',
              marginBottom: '0.5rem',
              backdropFilter: 'blur(4px)',
            }}
          >
            <span
              className="material-symbols-outlined"
              style={{ fontSize: '16px', color: 'var(--palette-moss-green, #889063)', fontVariationSettings: "'FILL' 1" }}
            >
              eco
            </span>
            <span
              style={{
                fontSize: '11px',
                fontWeight: 700,
                letterSpacing: '0.04em',
                textTransform: 'uppercase',
                color: 'var(--palette-tan, #CFBB99)',
              }}
            >
              FarmSathi Digital Agriculture
            </span>
          </div>

          <h1
            style={{
              fontSize: 'clamp(1.4rem, 3.5vw, 1.85rem)',
              fontWeight: 800,
              margin: '0 0 0.35rem 0',
              lineHeight: 1.2,
              letterSpacing: '-0.02em',
            }}
          >
            {farmerName}
          </h1>

          <p
            style={{
              fontSize: 'var(--font-size-sm)',
              color: 'rgba(229, 215, 196, 0.9)',
              margin: 0,
              maxWidth: '620px',
              lineHeight: 1.45,
            }}
          >
            {t.dashboard.heroSubtitle}
          </p>
        </div>

        {/* Integrated Natural Language Ask Input */}
        <form
          onSubmit={handleAskSubmit}
          style={{
            position: 'relative',
            zIndex: 2,
            display: 'flex',
            backgroundColor: 'var(--color-surface, #E5D7C4)',
            borderRadius: 'var(--radius-full)',
            padding: '0.35rem 0.45rem 0.35rem 1.15rem',
            boxShadow: '0 4px 14px rgba(53, 64, 36, 0.15)',
            alignItems: 'center',
            marginTop: '0.35rem',
            gap: '0.5rem',
          }}
        >
          <span
            className="material-symbols-outlined"
            style={{ color: 'var(--color-primary)', fontSize: '20px', flexShrink: 0 }}
          >
            forum
          </span>
          <input
            type="text"
            value={askQuery}
            onChange={(e) => setAskQuery(e.target.value)}
            placeholder={t.dashboard.askPlaceholder}
            style={{
              flex: 1,
              border: 'none',
              outline: 'none',
              fontSize: 'var(--font-size-sm)',
              color: 'var(--color-text-primary)',
              backgroundColor: 'transparent',
              minWidth: 0,
            }}
          />
          <button
            type="submit"
            style={{
              backgroundColor: 'var(--color-primary)',
              color: 'var(--color-text-inverse, #E5D7C4)',
              borderRadius: 'var(--radius-full)',
              padding: '0.5rem 1.1rem',
              fontWeight: 700,
              fontSize: 'var(--font-size-xs)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              cursor: 'pointer',
              flexShrink: 0,
              transition: 'background-color var(--transition-fast)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--color-primary-hover)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--color-primary)';
            }}
          >
            <span>{t.dashboard.askButton}</span>
            <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
              send
            </span>
          </button>
        </form>
      </section>

      {/* 2. Real Agro-Weather Section */}
      <Card padding="md">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.5rem',
            marginBottom: '1rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span
              className="material-symbols-outlined"
              style={{ color: 'var(--color-primary)', fontSize: '24px' }}
            >
              partly_cloudy_day
            </span>
            <h2
              style={{
                fontSize: 'var(--font-size-base)',
                fontWeight: 700,
                color: 'var(--color-text-primary)',
                margin: 0,
              }}
            >
              {t.weather.cardTitle}
            </h2>
          </div>

          {locationName ? (
            <Badge variant="primary" size="sm">
              📍 {locationName}
            </Badge>
          ) : (
            <Button
              size="sm"
              variant="outline"
              onClick={() => detectGpsLocation()}
              leftIcon={
                <span className="material-symbols-outlined" style={{ fontSize: '15px' }}>
                  my_location
                </span>
              }
            >
              {t.nav.detectLocation}
            </Button>
          )}
        </div>

        {weatherLoading ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem' }}>
            <Skeleton height="80px" borderRadius="var(--radius-lg)" />
            <Skeleton height="80px" borderRadius="var(--radius-lg)" />
            <Skeleton height="80px" borderRadius="var(--radius-lg)" />
            <Skeleton height="80px" borderRadius="var(--radius-lg)" />
          </div>
        ) : weatherData?.current ? (
          <div>
            {/* Live Weather Metrics Grid */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                gap: '0.75rem',
                marginBottom: '1rem',
              }}
            >
              {/* Temp */}
              <div
                style={{
                  backgroundColor: 'var(--color-surface-container-low)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: 'var(--radius-lg)',
                  padding: '0.85rem',
                  textAlign: 'center',
                }}
              >
                <span
                  className="material-symbols-outlined"
                  style={{ color: 'var(--color-primary)', fontSize: '22px' }}
                >
                  device_thermostat
                </span>
                <div
                  style={{
                    fontFamily: 'var(--font-tertiary)',
                    fontSize: 'var(--font-size-xl)',
                    fontWeight: 800,
                    color: 'var(--color-text-primary)',
                    marginTop: '0.2rem',
                    letterSpacing: '-0.02em',
                  }}
                >
                  {weatherData.current.temperature_celsius}°C
                </div>
                <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
                  {t.weather.temperature}
                </div>
              </div>

              {/* Condition */}
              <div
                style={{
                  backgroundColor: 'var(--color-surface-container-low)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: 'var(--radius-lg)',
                  padding: '0.85rem',
                  textAlign: 'center',
                }}
              >
                <span
                  className="material-symbols-outlined"
                  style={{ color: 'var(--color-primary)', fontSize: '22px' }}
                >
                  cloud
                </span>
                <div
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    fontWeight: 800,
                    color: 'var(--color-text-primary)',
                    marginTop: '0.35rem',
                  }}
                >
                  {weatherData.current.condition_text}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
                  Sky Outlook
                </div>
              </div>

              {/* Humidity */}
              <div
                style={{
                  backgroundColor: 'var(--color-surface-container-low)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: 'var(--radius-lg)',
                  padding: '0.85rem',
                  textAlign: 'center',
                }}
              >
                <span
                  className="material-symbols-outlined"
                  style={{ color: 'var(--color-primary)', fontSize: '22px' }}
                >
                  humidity_percentage
                </span>
                <div
                  style={{
                    fontFamily: 'var(--font-tertiary)',
                    fontSize: 'var(--font-size-xl)',
                    fontWeight: 800,
                    color: 'var(--color-text-primary)',
                    marginTop: '0.2rem',
                    letterSpacing: '-0.02em',
                  }}
                >
                  {weatherData.current.relative_humidity_percent}%
                </div>
                <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
                  {t.weather.humidity}
                </div>
              </div>

              {/* Rain */}
              <div
                style={{
                  backgroundColor: 'var(--color-surface-container-low)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: 'var(--radius-lg)',
                  padding: '0.85rem',
                  textAlign: 'center',
                }}
              >
                <span
                  className="material-symbols-outlined"
                  style={{ color: 'var(--color-primary)', fontSize: '22px' }}
                >
                  rainy
                </span>
                <div
                  style={{
                    fontFamily: 'var(--font-tertiary)',
                    fontSize: 'var(--font-size-xl)',
                    fontWeight: 800,
                    color: 'var(--color-text-primary)',
                    marginTop: '0.2rem',
                    letterSpacing: '-0.02em',
                  }}
                >
                  {weatherData.current.precipitation_mm} mm
                </div>
                <div style={{ fontSize: '11px', color: 'var(--color-text-secondary)', fontWeight: 600 }}>
                  {t.weather.rainfall}
                </div>
              </div>
            </div>

            {/* 7-Day Forecast Row */}
            {weatherData.forecast && weatherData.forecast.length > 0 && (
              <div>
                <div
                  style={{
                    fontSize: '12px',
                    fontWeight: 700,
                    color: 'var(--color-text-primary)',
                    marginBottom: '0.5rem',
                  }}
                >
                  {t.weather.forecast}
                </div>
                <div
                  style={{
                    display: 'flex',
                    gap: '0.5rem',
                    overflowX: 'auto',
                    paddingBottom: '0.35rem',
                  }}
                  className="hide-scrollbar"
                >
                  {weatherData.forecast.slice(0, 7).map((item, idx) => {
                    const d = new Date(item.date);
                    const dayLabel = d.toLocaleDateString(undefined, { weekday: 'short' });
                    return (
                      <div
                        key={idx}
                        style={{
                          flex: '0 0 auto',
                          minWidth: '85px',
                          backgroundColor: 'var(--color-surface-container-low)',
                          border: '1px solid var(--color-border-subtle)',
                          borderRadius: 'var(--radius-md)',
                          padding: '0.65rem 0.5rem',
                          textAlign: 'center',
                        }}
                      >
                        <div
                          style={{
                            fontSize: '11px',
                            fontWeight: 700,
                            color: 'var(--color-text-secondary)',
                          }}
                        >
                          {dayLabel}
                        </div>
                        <div
                          style={{
                            fontFamily: 'var(--font-tertiary)',
                            fontSize: 'var(--font-size-sm)',
                            fontWeight: 800,
                            color: 'var(--color-primary)',
                            margin: '0.2rem 0',
                          }}
                        >
                          {Math.round(item.temperature_max_celsius)}°
                        </div>
                        <div
                          style={{
                            fontSize: '10px',
                            color: 'var(--color-text-muted)',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                          }}
                        >
                          {item.condition_text}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        ) : (
          <EmptyState
            icon="location_off"
            title={t.weather.cardTitle}
            description={weatherError || t.weather.selectLocationPrompt}
            actionLabel={t.nav.detectLocation}
            onAction={() => detectGpsLocation()}
          />
        )}
      </Card>

      {/* 3. Core Agriculture Services Grid */}
      <section style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        <h2
          style={{
            fontSize: 'var(--font-size-base)',
            fontWeight: 800,
            color: 'var(--color-text-primary)',
            margin: 0,
            letterSpacing: '-0.01em',
          }}
        >
          {t.dashboard.quickActions}
        </h2>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '1rem',
          }}
        >
          {/* Card 1: Find Best Crop */}
          <Card
            hoverable
            onClick={() => onNavigate('crops')}
            style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: 'var(--radius-lg)',
                backgroundColor: 'var(--color-primary-light)',
                color: 'var(--color-primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: '24px' }}>
                psychology
              </span>
            </div>
            <div>
              <h3
                style={{
                  fontSize: 'var(--font-size-base)',
                  fontWeight: 700,
                  color: 'var(--color-text-primary)',
                  margin: '0 0 0.25rem 0',
                }}
              >
                {t.dashboard.actionCropRec}
              </h3>
              <p
                style={{
                  fontSize: 'var(--font-size-xs)',
                  color: 'var(--color-text-secondary)',
                  margin: 0,
                  lineHeight: 1.45,
                }}
              >
                {t.dashboard.actionCropRecDesc}
              </p>
            </div>
          </Card>

          {/* Card 2: Diagnose Foliar Disease */}
          <Card
            hoverable
            onClick={() => onNavigate('diagnosis')}
            style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: 'var(--radius-lg)',
                backgroundColor: 'var(--color-primary-light)',
                color: 'var(--color-primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: '24px' }}>
                photo_camera
              </span>
            </div>
            <div>
              <h3
                style={{
                  fontSize: 'var(--font-size-base)',
                  fontWeight: 700,
                  color: 'var(--color-text-primary)',
                  margin: '0 0 0.25rem 0',
                }}
              >
                {t.dashboard.actionDiagnosis}
              </h3>
              <p
                style={{
                  fontSize: 'var(--font-size-xs)',
                  color: 'var(--color-text-secondary)',
                  margin: 0,
                  lineHeight: 1.45,
                }}
              >
                {t.dashboard.actionDiagnosisDesc}
              </p>
            </div>
          </Card>

          {/* Card 3: Ask Advisor */}
          <Card
            hoverable
            onClick={() => onNavigate('ask')}
            style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: 'var(--radius-lg)',
                backgroundColor: 'var(--color-primary-light)',
                color: 'var(--color-primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: '24px' }}>
                forum
              </span>
            </div>
            <div>
              <h3
                style={{
                  fontSize: 'var(--font-size-base)',
                  fontWeight: 700,
                  color: 'var(--color-text-primary)',
                  margin: '0 0 0.25rem 0',
                }}
              >
                {t.dashboard.actionAsk}
              </h3>
              <p
                style={{
                  fontSize: 'var(--font-size-xs)',
                  color: 'var(--color-text-secondary)',
                  margin: 0,
                  lineHeight: 1.45,
                }}
              >
                {t.dashboard.actionAskDesc}
              </p>
            </div>
          </Card>

          {/* Card 4: My Crops */}
          <Card
            hoverable
            onClick={() => onNavigate('my-crops')}
            style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: 'var(--radius-lg)',
                backgroundColor: 'var(--color-primary-light)',
                color: 'var(--color-primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: '24px' }}>
                agriculture
              </span>
            </div>
            <div>
              <h3
                style={{
                  fontSize: 'var(--font-size-base)',
                  fontWeight: 700,
                  color: 'var(--color-text-primary)',
                  margin: '0 0 0.25rem 0',
                }}
              >
                {t.dashboard.actionMyCrops}
              </h3>
              <p
                style={{
                  fontSize: 'var(--font-size-xs)',
                  color: 'var(--color-text-secondary)',
                  margin: 0,
                  lineHeight: 1.45,
                }}
              >
                {t.dashboard.actionMyCropsDesc}
              </p>
            </div>
          </Card>
        </div>
      </section>

      {/* 4. Recent Farm Activity (Real data only, NO FAKE DATA) */}
      <Card padding="md">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '0.85rem',
          }}
        >
          <h2
            style={{
              fontSize: 'var(--font-size-base)',
              fontWeight: 700,
              color: 'var(--color-text-primary)',
              margin: 0,
            }}
          >
            {t.dashboard.recentActivity}
          </h2>
          {recentActivities.length > 0 && (
            <Button size="sm" variant="ghost" onClick={() => onNavigate('history')}>
              {t.dashboard.viewAll} →
            </Button>
          )}
        </div>

        {loadingHistory ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            <Skeleton height="48px" borderRadius="var(--radius-md)" />
            <Skeleton height="48px" borderRadius="var(--radius-md)" />
          </div>
        ) : recentActivities.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            {recentActivities.map((item, idx) => (
              <div
                key={item.id || idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.75rem 0.85rem',
                  backgroundColor: 'var(--color-surface-container-low)',
                  border: '1px solid var(--color-border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  transition: 'background-color var(--transition-fast)',
                }}
              >
                <div
                  style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: 'var(--color-primary-light)',
                    color: 'var(--color-primary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}
                >
                  <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
                    {item.module_type === 'crop'
                      ? 'psychology'
                      : item.module_type === 'disease'
                      ? 'photo_camera'
                      : 'forum'}
                  </span>
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: 'var(--font-size-sm)',
                      fontWeight: 700,
                      color: 'var(--color-text-primary)',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                  >
                    {item.title}
                  </div>
                  <div
                    style={{
                      fontSize: '11px',
                      color: 'var(--color-text-secondary)',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                  >
                    {item.subtitle}
                  </div>
                </div>
                <span
                  style={{
                    fontSize: '11px',
                    color: 'var(--color-text-muted)',
                    fontWeight: 600,
                    flexShrink: 0,
                  }}
                >
                  {handleFormatTime(item.created_at)}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            icon="history"
            title={t.dashboard.noActivity}
            description={t.dashboard.noActivityDesc}
            actionLabel={!isAuthenticated ? t.nav.login : undefined}
            onAction={!isAuthenticated ? onOpenAuth : undefined}
          />
        )}
      </Card>
    </div>
  );
};
