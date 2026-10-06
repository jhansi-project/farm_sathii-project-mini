import React, { useState } from 'react';
import { usePermissions } from '../../hooks/usePermissions';
import { useLocationStore } from '../../stores/locationStore';
import { useLanguageStore, SUPPORTED_LANGUAGES } from '../../stores/languageStore';
import { useTranslation } from '../../i18n/useTranslation';
import { LocationModal } from '../../components/layout/LocationModal';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';

interface PermissionSetupViewProps {
  onContinue: () => void;
  onBack?: () => void;
}

export const PermissionSetupView: React.FC<PermissionSetupViewProps> = ({
  onContinue,
  onBack,
}) => {
  const { t } = useTranslation();
  const { currentLanguage } = useLanguageStore();
  const {
    locationStatus,
    cameraStatus,
    micStatus,
    isCameraRequesting,
    isMicRequesting,
    requestCamera,
    requestMicrophone,
  } = usePermissions();

  const {
    detectGpsLocation,
    locationName,
    loading: locationLoading,
  } = useLocationStore();

  const [isLocationModalOpen, setIsLocationModalOpen] = useState(false);

  const handleAllowLocation = async () => {
    await detectGpsLocation();
  };

  const isLocationGranted = locationStatus === 'granted' || Boolean(locationName);
  const isCameraGranted = cameraStatus === 'granted';
  const isMicGranted = micStatus === 'granted';

  const currentLangObj =
    SUPPORTED_LANGUAGES.find((l) => l.code === currentLanguage) || SUPPORTED_LANGUAGES[0];

  return (
    <div
      style={{
        backgroundColor: 'var(--color-background)',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '1.5rem 1rem',
        maxWidth: '520px',
        margin: '0 auto',
        width: '100%',
        boxSizing: 'border-box',
      }}
    >
      {/* Top Header */}
      <header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          width: '100%',
          height: '44px',
        }}
      >
        {onBack ? (
          <button
            type="button"
            onClick={onBack}
            aria-label="Back"
            style={{
              width: '38px',
              height: '38px',
              borderRadius: 'var(--radius-full)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              color: 'var(--color-primary)',
              cursor: 'pointer',
              boxShadow: 'var(--shadow-xs)',
            }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
              arrow_back
            </span>
          </button>
        ) : (
          <div style={{ width: '38px' }} />
        )}

        <img
          src="/assets/farmsathi_logo.png"
          alt="FarmSathi"
          style={{
            height: '32px',
            width: 'auto',
            objectFit: 'contain',
            borderRadius: 'var(--radius-md)',
            display: 'block',
          }}
        />

        <Badge variant="primary" size="sm">
          {currentLangObj.nativeName}
        </Badge>
      </header>

      {/* Main Content Area */}
      <main
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '1rem',
          margin: '1rem 0',
          width: '100%',
        }}
      >
        {/* Title */}
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '32px', marginBottom: '0.25rem' }}>🌾</div>
          <h1
            style={{
              fontSize: 'var(--font-size-2xl)',
              fontWeight: 800,
              color: 'var(--color-primary)',
              margin: '0 0 0.35rem 0',
              letterSpacing: '-0.02em',
            }}
          >
            {t.permissions.title}
          </h1>
          <p
            style={{
              fontSize: 'var(--font-size-sm)',
              color: 'var(--color-text-secondary)',
              lineHeight: 1.45,
              maxWidth: '400px',
              margin: '0 auto',
            }}
          >
            {t.permissions.subtitle}
          </p>
        </div>

        {/* Permissions Cards Stack */}
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {/* 1. Location Permission */}
          <Card padding="md">
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.85rem' }}>
              <div
                style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: 'var(--radius-lg)',
                  backgroundColor: isLocationGranted
                    ? 'var(--color-success-bg)'
                    : 'var(--color-primary-light)',
                  color: isLocationGranted ? 'var(--color-success)' : 'var(--color-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: '24px' }}>
                  location_on
                </span>
              </div>

              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem' }}>
                  <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, margin: 0 }}>
                    {t.permissions.locationTitle}
                  </h3>
                  {isLocationGranted ? (
                    <Badge variant="success" size="sm">
                      {t.permissions.locationEnabled}
                    </Badge>
                  ) : (
                    <Badge variant="neutral" size="sm">
                      {t.permissions.optionalBadge}
                    </Badge>
                  )}
                </div>

                <p
                  style={{
                    fontSize: 'var(--font-size-xs)',
                    color: 'var(--color-text-secondary)',
                    margin: '0.25rem 0 0.65rem 0',
                    lineHeight: 1.4,
                  }}
                >
                  {locationName ? `📍 ${locationName}` : t.permissions.locationDesc}
                </p>

                {!isLocationGranted && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <Button
                      size="sm"
                      onClick={handleAllowLocation}
                      isLoading={locationLoading}
                      leftIcon={
                        <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
                          my_location
                        </span>
                      }
                    >
                      {locationLoading ? t.permissions.locationDetecting : t.permissions.locationAllow}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setIsLocationModalOpen(true)}
                    >
                      {t.permissions.locationManualOption}
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </Card>

          {/* 2. Camera Permission */}
          <Card padding="md">
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.85rem' }}>
              <div
                style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: 'var(--radius-lg)',
                  backgroundColor: isCameraGranted
                    ? 'var(--color-success-bg)'
                    : 'var(--color-primary-light)',
                  color: isCameraGranted ? 'var(--color-success)' : 'var(--color-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: '24px' }}>
                  photo_camera
                </span>
              </div>

              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem' }}>
                  <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, margin: 0 }}>
                    {t.permissions.cameraTitle}
                  </h3>
                  {isCameraGranted ? (
                    <Badge variant="success" size="sm">
                      {t.permissions.cameraEnabled}
                    </Badge>
                  ) : (
                    <Badge variant="neutral" size="sm">
                      {t.permissions.optionalBadge}
                    </Badge>
                  )}
                </div>

                <p
                  style={{
                    fontSize: 'var(--font-size-xs)',
                    color: 'var(--color-text-secondary)',
                    margin: '0.25rem 0 0.65rem 0',
                    lineHeight: 1.4,
                  }}
                >
                  {t.permissions.cameraDesc}
                </p>

                {!isCameraGranted && (
                  <Button
                    size="sm"
                    onClick={requestCamera}
                    isLoading={isCameraRequesting}
                    leftIcon={
                      <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
                        camera
                      </span>
                    }
                  >
                    {t.permissions.cameraAllow}
                  </Button>
                )}
              </div>
            </div>
          </Card>

          {/* 3. Microphone Permission */}
          <Card padding="md">
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.85rem' }}>
              <div
                style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: 'var(--radius-lg)',
                  backgroundColor: isMicGranted
                    ? 'var(--color-success-bg)'
                    : 'var(--color-primary-light)',
                  color: isMicGranted ? 'var(--color-success)' : 'var(--color-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: '24px' }}>
                  mic
                </span>
              </div>

              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem' }}>
                  <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, margin: 0 }}>
                    {t.permissions.micTitle}
                  </h3>
                  {isMicGranted ? (
                    <Badge variant="success" size="sm">
                      {t.permissions.micEnabled}
                    </Badge>
                  ) : (
                    <Badge variant="neutral" size="sm">
                      {t.permissions.optionalBadge}
                    </Badge>
                  )}
                </div>

                <p
                  style={{
                    fontSize: 'var(--font-size-xs)',
                    color: 'var(--color-text-secondary)',
                    margin: '0.25rem 0 0.65rem 0',
                    lineHeight: 1.4,
                  }}
                >
                  {t.permissions.micDesc}
                </p>

                {!isMicGranted && (
                  <Button
                    size="sm"
                    onClick={requestMicrophone}
                    isLoading={isMicRequesting}
                    leftIcon={
                      <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
                        mic
                      </span>
                    }
                  >
                    {t.permissions.micAllow}
                  </Button>
                )}
              </div>
            </div>
          </Card>
        </div>

        <p
          style={{
            fontSize: '11px',
            color: 'var(--color-text-muted)',
            textAlign: 'center',
            margin: '0.25rem 0 0 0',
            lineHeight: 1.4,
          }}
        >
          {t.permissions.optionalNotice}
        </p>
      </main>

      {/* Action Footer */}
      <footer
        style={{
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem',
          marginTop: 'auto',
          paddingTop: '0.5rem',
        }}
      >
        <Button
          type="button"
          size="lg"
          fullWidth
          onClick={onContinue}
          rightIcon={
            <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
              arrow_forward
            </span>
          }
        >
          {t.permissions.continue}
        </Button>

        <button
          type="button"
          onClick={onContinue}
          style={{
            padding: '0.5rem',
            fontSize: 'var(--font-size-sm)',
            color: 'var(--color-text-secondary)',
            fontWeight: 600,
            cursor: 'pointer',
            textAlign: 'center',
          }}
        >
          {t.permissions.skipForNow}
        </button>
      </footer>

      {/* Manual Location Search Dialog */}
      <LocationModal
        isOpen={isLocationModalOpen}
        onClose={() => setIsLocationModalOpen(false)}
      />
    </div>
  );
};
