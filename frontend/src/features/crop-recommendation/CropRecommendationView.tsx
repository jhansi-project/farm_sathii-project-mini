import React, { useState } from 'react';
import { cropService } from '../../services/cropService';
import { weatherService } from '../../services/weatherService';
import { useLocationStore } from '../../stores/locationStore';
import { useTranslation } from '../../i18n/useTranslation';
import { CropRecommendationPayload, CropRecommendationResult } from '../../types/crop';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';

const CROP_ICONS: Record<string, string> = {
  rice: '🌾',
  wheat: '🌾',
  cotton: '🌿',
  maize: '🌽',
  chickpea: '🌱',
  kidneybeans: '🫘',
  pigeonpeas: '🫘',
  mothbeans: '🫘',
  mungbean: '🫘',
  blackgram: '🫘',
  lentil: '🫘',
  pomegranate: '🪴',
  banana: '🍌',
  mango: '🥭',
  grapes: '🍇',
  watermelon: '🍉',
  muskmelon: '🍈',
  apple: '🍎',
  orange: '🍊',
  papaya: '🍈',
  coconut: '🥥',
  jute: '🎋',
  coffee: '☕',
};

export const CropRecommendationView: React.FC = () => {
  const { t } = useTranslation();
  const { locationName, latitude, longitude } = useLocationStore();

  // Form State: opens with empty strings — no fabricated defaults
  const [nVal, setNVal] = useState<string>('');
  const [pVal, setPVal] = useState<string>('');
  const [kVal, setKVal] = useState<string>('');
  const [tempVal, setTempVal] = useState<string>('');
  const [humVal, setHumVal] = useState<string>('');
  const [phVal, setPhVal] = useState<string>('');
  const [rainVal, setRainVal] = useState<string>('');

  // UI States
  const [loading, setLoading] = useState(false);
  const [autoFilling, setAutoFilling] = useState(false);
  const [result, setResult] = useState<CropRecommendationResult | null>(null);
  const [submittedInputs, setSubmittedInputs] = useState<CropRecommendationPayload | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const handleFillWeather = async () => {
    if (latitude === null || longitude === null) {
      setErrorMessage(t.weather.selectLocationPrompt);
      return;
    }
    setAutoFilling(true);
    setErrorMessage(null);
    try {
      const data = await weatherService.getCurrentWeather(latitude, longitude);
      if (data.current) {
        setTempVal(data.current.temperature_celsius.toString());
        setHumVal(data.current.relative_humidity_percent.toString());
        if (data.current.precipitation_mm > 0) {
          setRainVal((data.current.precipitation_mm * 10).toFixed(0));
        }
      }
    } catch {
      setErrorMessage('Could not load current weather values. Please enter them manually.');
    } finally {
      setAutoFilling(false);
    }
  };

  const validate = (): boolean => {
    const errors: Record<string, string> = {};

    const n = parseFloat(nVal);
    if (!nVal || isNaN(n)) {
      errors.N = 'Please enter soil Nitrogen value';
    } else if (n < 0 || n > 250) {
      errors.N = 'Nitrogen must be between 0 and 250 kg/ha';
    }

    const p = parseFloat(pVal);
    if (!pVal || isNaN(p)) {
      errors.P = 'Please enter soil Phosphorus value';
    } else if (p < 0 || p > 200) {
      errors.P = 'Phosphorus must be between 0 and 200 kg/ha';
    }

    const k = parseFloat(kVal);
    if (!kVal || isNaN(k)) {
      errors.K = 'Please enter soil Potassium value';
    } else if (k < 0 || k > 250) {
      errors.K = 'Potassium must be between 0 and 250 kg/ha';
    }

    const temp = parseFloat(tempVal);
    if (!tempVal || isNaN(temp)) {
      errors.temperature = 'Please enter temperature';
    } else if (temp < 0 || temp > 60) {
      errors.temperature = 'Temperature must be between 0°C and 60°C';
    }

    const hum = parseFloat(humVal);
    if (!humVal || isNaN(hum)) {
      errors.humidity = 'Please enter humidity';
    } else if (hum < 0 || hum > 100) {
      errors.humidity = 'Humidity must be between 0% and 100%';
    }

    const ph = parseFloat(phVal);
    if (!phVal || isNaN(ph)) {
      errors.ph = 'Please enter soil pH';
    } else if (ph < 0 || ph > 14) {
      errors.ph = 'pH must be between 0 and 14';
    }

    const rain = parseFloat(rainVal);
    if (!rainVal || isNaN(rain)) {
      errors.rainfall = 'Please enter expected rainfall';
    } else if (rain < 0 || rain > 5000) {
      errors.rainfall = 'Rainfall must be between 0 and 5000 mm';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    setErrorMessage(null);

    const payload: CropRecommendationPayload = {
      N: parseFloat(nVal),
      P: parseFloat(pVal),
      K: parseFloat(kVal),
      temperature: parseFloat(tempVal),
      humidity: parseFloat(humVal),
      ph: parseFloat(phVal),
      rainfall: parseFloat(rainVal),
    };

    try {
      const res = await cropService.getRecommendation(payload);
      setResult(res);
      setSubmittedInputs(payload);
    } catch (err: any) {
      if (!err.response) {
        setErrorMessage(
          'Unable to reach the FarmSathi server. Please check your network connection.'
        );
      } else {
        const detail = err.response?.data?.detail;
        if (typeof detail === 'string') {
          setErrorMessage(detail);
        } else if (Array.isArray(detail)) {
          const msgs = detail.map((d: any) => d.msg || d.message).filter(Boolean);
          setErrorMessage(msgs.join(', ') || 'Invalid inputs. Please verify soil and climate values.');
        } else {
          setErrorMessage('Unable to calculate crop recommendation right now. Please check your inputs.');
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setSubmittedInputs(null);
    setErrorMessage(null);
  };

  const cropKey = (result?.recommended_crop || '').toLowerCase();
  const cropEmoji = CROP_ICONS[cropKey] || '🌱';

  return (
    <div className="farmsathi-page-container-narrow">
      {/* Header */}
      <PageHeader
        icon="psychology"
        title={t.cropRec.title}
        subtitle={t.cropRec.subtitle}
        badge={
          locationName ? (
            <Badge variant="primary" size="sm">
              📍 {locationName}
            </Badge>
          ) : undefined
        }
      />

      {/* Error Banner */}
      {errorMessage && (
        <div
          style={{
            backgroundColor: 'var(--color-error-bg)',
            color: 'var(--color-error)',
            border: '1px solid var(--color-error-border)',
            padding: '0.85rem 1rem',
            borderRadius: 'var(--radius-lg)',
            fontSize: 'var(--font-size-sm)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
          }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
            error
          </span>
          <span style={{ flex: 1 }}>{errorMessage}</span>
          <button
            type="button"
            onClick={() => setErrorMessage(null)}
            style={{ color: 'var(--color-error)', cursor: 'pointer' }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
              close
            </span>
          </button>
        </div>
      )}

      {!result ? (
        /* Empty Input Form */
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Card 1: Soil Nutrients */}
          <Card padding="lg">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
              <span className="material-symbols-outlined" style={{ color: 'var(--color-primary)', fontSize: '22px' }}>
                science
              </span>
              <h2 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
                {t.cropRec.soilNutrients} (NPK kg/ha)
              </h2>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
              <Input
                label={`${t.cropRec.nitrogen} (N)`}
                type="number"
                step="any"
                value={nVal}
                onChange={(e) => setNVal(e.target.value)}
                placeholder={t.cropRec.nitrogenPlaceholder || 'e.g. 90'}
                error={validationErrors.N}
                helperText="Typical range: 0 - 250 kg/ha"
              />

              <Input
                label={`${t.cropRec.phosphorus} (P)`}
                type="number"
                step="any"
                value={pVal}
                onChange={(e) => setPVal(e.target.value)}
                placeholder={t.cropRec.phosphorusPlaceholder || 'e.g. 42'}
                error={validationErrors.P}
                helperText="Typical range: 0 - 200 kg/ha"
              />

              <Input
                label={`${t.cropRec.potassium} (K)`}
                type="number"
                step="any"
                value={kVal}
                onChange={(e) => setKVal(e.target.value)}
                placeholder={t.cropRec.potassiumPlaceholder || 'e.g. 43'}
                error={validationErrors.K}
                helperText="Typical range: 0 - 250 kg/ha"
              />
            </div>
          </Card>

          {/* Card 2: Climate & Soil Parameters */}
          <Card padding="lg">
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '0.5rem',
                marginBottom: '1.25rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className="material-symbols-outlined" style={{ color: 'var(--color-primary)', fontSize: '22px' }}>
                  thermostat
                </span>
                <h2 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
                  {t.cropRec.climateConditions}
                </h2>
              </div>

              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={handleFillWeather}
                isLoading={autoFilling}
                leftIcon={
                  <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
                    cloud_download
                  </span>
                }
              >
                {t.cropRec.fillFromWeather}
              </Button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
              <Input
                label={`${t.cropRec.temperature} (°C)`}
                type="number"
                step="any"
                value={tempVal}
                onChange={(e) => setTempVal(e.target.value)}
                placeholder={t.cropRec.temperaturePlaceholder || 'e.g. 26.5'}
                error={validationErrors.temperature}
              />

              <Input
                label={`${t.cropRec.humidity} (%)`}
                type="number"
                step="any"
                value={humVal}
                onChange={(e) => setHumVal(e.target.value)}
                placeholder={t.cropRec.humidityPlaceholder || 'e.g. 78'}
                error={validationErrors.humidity}
              />

              <Input
                label={`${t.cropRec.ph} (pH 0-14)`}
                type="number"
                step="any"
                value={phVal}
                onChange={(e) => setPhVal(e.target.value)}
                placeholder={t.cropRec.phPlaceholder || 'e.g. 6.5'}
                error={validationErrors.ph}
                helperText="Optimal soil range: 5.5 - 7.5"
              />

              <Input
                label={`${t.cropRec.rainfall} (mm)`}
                type="number"
                step="any"
                value={rainVal}
                onChange={(e) => setRainVal(e.target.value)}
                placeholder={t.cropRec.rainfallPlaceholder || 'e.g. 200'}
                error={validationErrors.rainfall}
              />
            </div>
          </Card>

          {/* Submit Action */}
          <Button
            type="submit"
            size="lg"
            fullWidth
            isLoading={loading}
            leftIcon={
              <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
                auto_awesome
              </span>
            }
          >
            {loading ? t.cropRec.calculating : t.cropRec.calculateButton}
          </Button>
        </form>
      ) : (
        /* Result Presentation */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <Card
            padding="lg"
            style={{
              textAlign: 'center',
              border: '2px solid var(--color-primary-subtle)',
              backgroundColor: 'var(--color-surface)',
            }}
          >
            <div style={{ fontSize: '56px', lineHeight: 1, marginBottom: '0.75rem' }}>
              {cropEmoji}
            </div>

            <Badge variant="success" size="md" style={{ marginBottom: '0.65rem' }}>
              Recommended Optimal Crop
            </Badge>

            <h2
              style={{
                fontFamily: 'var(--font-secondary)',
                fontSize: 'clamp(1.75rem, 4vw, 2.25rem)',
                fontWeight: 800,
                color: 'var(--color-primary)',
                margin: '0 0 0.5rem 0',
                letterSpacing: '-0.02em',
                textTransform: 'capitalize',
              }}
            >
              {result.recommended_crop}
            </h2>

            <p
              style={{
                fontSize: 'var(--font-size-sm)',
                color: 'var(--color-text-secondary)',
                maxWidth: '480px',
                margin: '0 auto 1.5rem auto',
                lineHeight: 1.5,
              }}
            >
              Based on your specific soil nutrients (N-P-K), pH balance, and climatic parameters, this crop demonstrates highest viability and yield potential.
            </p>

            {/* Context Metrics Summary */}
            {submittedInputs && (
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))',
                  gap: '0.5rem',
                  padding: '1rem',
                  backgroundColor: 'var(--color-surface-container-low)',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid var(--color-border-subtle)',
                  marginBottom: '1.5rem',
                }}
              >
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontWeight: 600 }}>N-P-K</div>
                  <div style={{ fontFamily: 'var(--font-tertiary)', fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                    {submittedInputs.N}-{submittedInputs.P}-{submittedInputs.K}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontWeight: 600 }}>Temp</div>
                  <div style={{ fontFamily: 'var(--font-tertiary)', fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                    {submittedInputs.temperature}°C
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontWeight: 600 }}>Humidity</div>
                  <div style={{ fontFamily: 'var(--font-tertiary)', fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                    {submittedInputs.humidity}%
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontWeight: 600 }}>Soil pH</div>
                  <div style={{ fontFamily: 'var(--font-tertiary)', fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                    {submittedInputs.ph}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', fontWeight: 600 }}>Rainfall</div>
                  <div style={{ fontFamily: 'var(--font-tertiary)', fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                    {submittedInputs.rainfall} mm
                  </div>
                </div>
              </div>
            )}

            <Button
              type="button"
              variant="outline"
              onClick={handleReset}
              leftIcon={
                <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                  refresh
                </span>
              }
            >
              {t.cropRec.checkAnother}
            </Button>
          </Card>
        </div>
      )}
    </div>
  );
};
