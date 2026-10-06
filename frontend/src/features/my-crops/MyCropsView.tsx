import React, { useState, useEffect } from 'react';
import { historyService } from '../../services/historyService';
import { useAuthStore } from '../../stores/authStore';
import { useTranslation } from '../../i18n/useTranslation';
import { CropRecommendationHistoryItem } from '../../types/crop';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { Input } from '../../components/ui/Input';
import { EmptyState } from '../../components/ui/EmptyState';
import { Skeleton } from '../../components/ui/Skeleton';

interface UserTrackedCrop {
  id: string;
  name: string;
  plantedDate: string;
  stage: string;
  notes?: string;
}

const STORAGE_KEY = 'farmsathi_user_crops';

const loadSavedCrops = (): UserTrackedCrop[] => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    // Ignore
  }
  return [];
};

export const MyCropsView: React.FC = () => {
  const { t } = useTranslation();
  const { isAuthenticated } = useAuthStore();

  const [trackedCrops, setTrackedCrops] = useState<UserTrackedCrop[]>(loadSavedCrops());
  const [historyCrops, setHistoryCrops] = useState<CropRecommendationHistoryItem[]>([]);
  const [loading, setLoading] = useState(false);

  // Modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [cropName, setCropName] = useState('');
  const [plantingStage, setPlantingStage] = useState('Vegetative / Tillering');

  useEffect(() => {
    if (!isAuthenticated) {
      setHistoryCrops([]);
      return;
    }

    let isMounted = true;
    const fetchHistory = async () => {
      setLoading(true);
      try {
        const res = await historyService.getCropHistory(0, 10);
        if (isMounted && res?.items) {
          setHistoryCrops(res.items);
        }
      } catch {
        if (isMounted) setHistoryCrops([]);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchHistory();
    return () => {
      isMounted = false;
    };
  }, [isAuthenticated]);

  const handleAddCrop = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cropName.trim()) return;

    const newCrop: UserTrackedCrop = {
      id: `crop-${Date.now()}`,
      name: cropName.trim(),
      plantedDate: new Date().toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }),
      stage: plantingStage,
    };

    const updated = [newCrop, ...trackedCrops];
    setTrackedCrops(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    setCropName('');
    setShowAddModal(false);
  };

  const handleRemoveCrop = (id: string) => {
    const updated = trackedCrops.filter((c) => c.id !== id);
    setTrackedCrops(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  };

  const hasAnyCrops = trackedCrops.length > 0 || historyCrops.length > 0;

  return (
    <div className="farmsathi-page-container" style={{ paddingBottom: '6rem' }}>
      {/* Header & Primary Action */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '1.5rem' }}>
        <PageHeader
          title={t.myCrops.title}
          subtitle={t.myCrops.subtitle}
          icon="agriculture"
        />

        <Button
          variant="primary"
          size="md"
          onClick={() => setShowAddModal(true)}
          leftIcon={<span className="material-symbols-outlined" style={{ fontSize: '18px' }}>add</span>}
        >
          {t.myCrops.addCrop}
        </Button>
      </div>

      {/* Main Content Area */}
      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <Skeleton height="80px" borderRadius="var(--radius-lg)" />
          <Skeleton height="80px" borderRadius="var(--radius-lg)" />
          <Skeleton height="80px" borderRadius="var(--radius-lg)" />
        </div>
      ) : hasAnyCrops ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Active Farmer-Tracked Crops */}
          {trackedCrops.length > 0 && (
            <section>
              <h2 style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '0.75rem' }}>
                {t.myCrops.activeCrops || 'Active Farm Plantings'} ({trackedCrops.length})
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {trackedCrops.map((crop) => (
                  <Card
                    key={crop.id}
                    hoverable
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '1.15rem 1.25rem',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <div
                        style={{
                          width: '46px',
                          height: '46px',
                          borderRadius: 'var(--radius-md)',
                          backgroundColor: 'var(--color-primary-light)',
                          color: 'var(--color-primary)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '22px',
                          flexShrink: 0,
                        }}
                      >
                        🌾
                      </div>
                      <div>
                        <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 0.25rem 0' }}>
                          {crop.name}
                        </h3>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                          <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)' }}>
                            {t.myCrops.plantedOn}: <strong>{crop.plantedDate}</strong>
                          </span>
                          <span style={{ color: 'var(--color-border)' }}>•</span>
                          <Badge variant="primary" size="sm">
                            {crop.stage}
                          </Badge>
                        </div>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => handleRemoveCrop(crop.id)}
                      title="Remove crop"
                      style={{
                        color: 'var(--color-text-tertiary)',
                        padding: '0.45rem',
                        borderRadius: 'var(--radius-full)',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'color var(--transition-fast)',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--color-error)')}
                      onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--color-text-tertiary)')}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
                        delete_outline
                      </span>
                    </button>
                  </Card>
                ))}
              </div>
            </section>
          )}

          {/* AI Recommended Crops from History */}
          {historyCrops.length > 0 && (
            <section style={{ marginTop: trackedCrops.length > 0 ? '0.75rem' : '0' }}>
              <h2 style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '0.75rem' }}>
                {t.cropRec.title || 'AI Recommended for Your Soil'} ({historyCrops.length})
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {historyCrops.map((item) => (
                  <Card
                    key={item.id}
                    hoverable
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '1.15rem 1.25rem',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <div
                        style={{
                          width: '46px',
                          height: '46px',
                          borderRadius: 'var(--radius-md)',
                          backgroundColor: 'var(--color-surface-sunken)',
                          color: 'var(--color-primary)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '22px',
                          flexShrink: 0,
                        }}
                      >
                        🌱
                      </div>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                          <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0, textTransform: 'capitalize' }}>
                            {item.recommended_crop}
                          </h3>
                          <Badge variant="success" size="sm">
                            AI Recommended
                          </Badge>
                        </div>
                        <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>
                          Soil: N={item.inputs.N}, P={item.inputs.P}, K={item.inputs.K} • pH={item.inputs.ph}
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </section>
          )}
        </div>
      ) : (
        /* Symmetrical Empty State */
        <EmptyState
          icon="agriculture"
          title={t.myCrops.emptyTitle}
          description={t.myCrops.emptySubtitle}
          actionLabel={t.myCrops.addCrop}
          onAction={() => setShowAddModal(true)}
        />
      )}

      {/* Add Crop Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title={t.myCrops.addCrop}
      >
        <form onSubmit={handleAddCrop} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <Input
            label={t.myCrops.cropName}
            placeholder={t.myCrops.cropNamePlaceholder}
            value={cropName}
            onChange={(e) => setCropName(e.target.value)}
            required
            autoFocus
          />

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            <label style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
              Growth Stage
            </label>
            <select
              value={plantingStage}
              onChange={(e) => setPlantingStage(e.target.value)}
              style={{
                width: '100%',
                minHeight: '44px',
                padding: '0.65rem 0.85rem',
                borderRadius: 'var(--radius-md)',
                border: '1.5px solid var(--color-border)',
                backgroundColor: 'var(--color-surface)',
                fontSize: 'var(--font-size-sm)',
                color: 'var(--color-text-primary)',
                outline: 'none',
              }}
            >
              <option value="Sowing / Germination">Sowing / Germination</option>
              <option value="Seedling">Seedling</option>
              <option value="Vegetative / Tillering">Vegetative / Tillering</option>
              <option value="Flowering / Heading">Flowering / Heading</option>
              <option value="Maturity / Harvesting">Maturity / Harvesting</option>
            </select>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowAddModal(false)}
            >
              {t.common.cancel}
            </Button>
            <Button
              type="submit"
              variant="primary"
            >
              {t.common.save}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
