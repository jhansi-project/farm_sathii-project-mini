import React from 'react';
import { useLanguageStore, SUPPORTED_LANGUAGES } from '../../stores/languageStore';
import { useTranslation } from '../../i18n/useTranslation';
import { Button } from '../../components/ui/Button';

interface WelcomeViewProps {
  onContinue: () => void;
}

export const WelcomeView: React.FC<WelcomeViewProps> = ({ onContinue }) => {
  const { currentLanguage, setLanguage, completeWelcome } = useLanguageStore();
  const { t } = useTranslation();

  const handleContinue = () => {
    completeWelcome();
    onContinue();
  };

  return (
    <div
      style={{
        backgroundColor: 'var(--color-background)',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '1.75rem 1rem',
        maxWidth: '540px',
        margin: '0 auto',
        width: '100%',
        boxSizing: 'border-box',
      }}
    >
      {/* Branding Header */}
      <header
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
        }}
      >
        <img
          src="/assets/farmsathi_logo.png"
          alt="FarmSathi"
          style={{
            height: '56px',
            width: 'auto',
            maxWidth: '220px',
            objectFit: 'contain',
            borderRadius: 'var(--radius-lg)',
            display: 'block',
            marginBottom: '0.65rem',
            boxShadow: 'var(--shadow-sm)',
          }}
        />
        <p
          style={{
            fontSize: 'var(--font-size-sm)',
            fontWeight: 600,
            color: 'var(--color-text-secondary)',
            marginTop: '0.25rem',
          }}
        >
          {t.welcome.tagline}
        </p>
      </header>

      {/* Main Content Area */}
      <main
        style={{
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '1.25rem',
          margin: '1.25rem 0',
        }}
      >
        {/* Authentic Agricultural Hero Card */}
        <div
          style={{
            width: '100%',
            height: '190px',
            borderRadius: 'var(--radius-xl)',
            overflow: 'hidden',
            position: 'relative',
            backgroundColor: 'var(--color-surface)',
            boxShadow: 'var(--shadow-sm)',
            border: '1px solid var(--color-border)',
          }}
        >
          <img
            src="/assets/rice_harvest.jpg"
            alt="Farmers harvesting rice in field"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              objectPosition: 'center 35%',
            }}
          />
          <div
            style={{
              position: 'absolute',
              inset: 0,
              background: 'linear-gradient(to top, rgba(53, 64, 36, 0.88) 0%, rgba(53, 64, 36, 0) 65%)',
              display: 'flex',
              alignItems: 'flex-end',
              padding: '1rem',
            }}
          >
            <span
              style={{
                color: 'var(--color-text-inverse, #E5D7C4)',
                fontSize: 'var(--font-size-xs)',
                fontWeight: 700,
                letterSpacing: '0.02em',
                textShadow: '0 1px 3px rgba(0,0,0,0.5)',
              }}
            >
              🌱 Digital Agriculture for Every Indian Farmer
            </span>
          </div>
        </div>

        {/* Clear Value Proposition */}
        <p
          style={{
            fontSize: 'var(--font-size-sm)',
            color: 'var(--color-text-secondary)',
            textAlign: 'center',
            lineHeight: 1.5,
            maxWidth: '460px',
            margin: 0,
          }}
        >
          {t.welcome.description}
        </p>

        {/* 3 Core Pillars */}
        <div
          style={{
            width: '100%',
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '0.65rem',
          }}
        >
          <div
            style={{
              backgroundColor: 'var(--color-surface)',
              padding: '0.75rem 0.5rem',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--color-border-subtle)',
              textAlign: 'center',
              boxShadow: 'var(--shadow-xs)',
            }}
          >
            <span className="material-symbols-outlined" style={{ color: 'var(--color-primary)', fontSize: '24px' }}>
              psychology
            </span>
            <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-text-primary)', marginTop: '0.25rem' }}>
              {t.welcome.cropRec}
            </div>
          </div>
          <div
            style={{
              backgroundColor: 'var(--color-surface)',
              padding: '0.75rem 0.5rem',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--color-border-subtle)',
              textAlign: 'center',
              boxShadow: 'var(--shadow-xs)',
            }}
          >
            <span className="material-symbols-outlined" style={{ color: 'var(--color-primary)', fontSize: '24px' }}>
              photo_camera
            </span>
            <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-text-primary)', marginTop: '0.25rem' }}>
              {t.welcome.disease}
            </div>
          </div>
          <div
            style={{
              backgroundColor: 'var(--color-surface)',
              padding: '0.75rem 0.5rem',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--color-border-subtle)',
              textAlign: 'center',
              boxShadow: 'var(--shadow-xs)',
            }}
          >
            <span className="material-symbols-outlined" style={{ color: 'var(--color-primary)', fontSize: '24px' }}>
              rainy
            </span>
            <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-text-primary)', marginTop: '0.25rem' }}>
              {t.welcome.weather}
            </div>
          </div>
        </div>

        {/* Tactile Native Language Selector Grid */}
        <div
          style={{
            width: '100%',
            backgroundColor: 'var(--color-surface)',
            borderRadius: 'var(--radius-xl)',
            padding: '1.25rem',
            boxShadow: 'var(--shadow-xs)',
            border: '1px solid var(--color-border)',
            boxSizing: 'border-box',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              fontSize: 'var(--font-size-sm)',
              fontWeight: 700,
              color: 'var(--color-primary)',
              marginBottom: '0.85rem',
            }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
              translate
            </span>
            <span>{t.welcome.selectLanguagePrompt}</span>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '0.65rem',
            }}
          >
            {SUPPORTED_LANGUAGES.map((lang) => {
              const isSelected = currentLanguage === lang.code;
              return (
                <button
                  key={lang.code}
                  type="button"
                  onClick={() => setLanguage(lang.code)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.75rem 0.85rem',
                    borderRadius: 'var(--radius-lg)',
                    border: `1.5px solid ${
                      isSelected ? 'var(--color-primary)' : 'var(--color-border)'
                    }`,
                    backgroundColor: isSelected
                      ? 'var(--color-primary-light)'
                      : 'var(--color-surface)',
                    cursor: 'pointer',
                    transition: 'all var(--transition-fast)',
                    textAlign: 'left',
                  }}
                  onMouseEnter={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.backgroundColor = 'var(--color-surface-container-low)';
                      e.currentTarget.style.borderColor = 'var(--color-primary-subtle)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.backgroundColor = 'var(--color-surface)';
                      e.currentTarget.style.borderColor = 'var(--color-border)';
                    }
                  }}
                >
                  <div>
                    <div
                      style={{
                        fontSize: 'var(--font-size-sm)',
                        fontWeight: 700,
                        color: isSelected ? 'var(--color-primary)' : 'var(--color-text-primary)',
                        lineHeight: 1.3,
                      }}
                    >
                      {lang.nativeName}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                      {lang.name}
                    </div>
                  </div>
                  <span
                    className="material-symbols-outlined"
                    style={{
                      fontSize: '20px',
                      color: isSelected ? 'var(--color-primary)' : 'var(--color-border)',
                      fontVariationSettings: isSelected ? "'FILL' 1" : "'FILL' 0",
                    }}
                  >
                    {isSelected ? 'check_circle' : 'radio_button_unchecked'}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </main>

      {/* Action Footer */}
      <footer style={{ width: '100%', marginTop: 'auto', paddingTop: '0.5rem' }}>
        <Button
          type="button"
          size="lg"
          fullWidth
          onClick={handleContinue}
          rightIcon={
            <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
              arrow_forward
            </span>
          }
        >
          {t.welcome.continueButton}
        </Button>
      </footer>
    </div>
  );
};
