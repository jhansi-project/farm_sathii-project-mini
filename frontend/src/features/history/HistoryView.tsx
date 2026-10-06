import React, { useState, useEffect, useCallback } from 'react';
import { historyService } from '../../services/historyService';
import { useAuthStore } from '../../stores/authStore';
import { CropRecommendationHistoryItem } from '../../types/crop';
import { DiseaseHistoryItem } from '../../types/disease';
import { AdvisoryConversationDetail, AdvisoryConversationSummary } from '../../types/advisory';
import { UnifiedHistoryItem } from '../../types/history';
import { useTranslation } from '../../i18n/useTranslation';
import { AppNavTab } from '../dashboard/DashboardView';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { EmptyState } from '../../components/ui/EmptyState';
import { Skeleton } from '../../components/ui/Skeleton';
import { PageHeader } from '../../components/layout/PageHeader';

type HistoryFilter = 'all' | 'disease' | 'crop' | 'queries';

interface HistoryViewProps {
  onNavigate?: (tab: AppNavTab, queryContext?: string, conversationId?: string) => void;
  onOpenAuth?: () => void;
}

export const HistoryView: React.FC<HistoryViewProps> = ({ onNavigate, onOpenAuth }) => {
  const { t } = useTranslation();
  const { user } = useAuthStore();
  const isAuthenticated = Boolean(user);

  const [filter, setFilter] = useState<HistoryFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearch, setShowSearch] = useState(false);

  // Data states
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [unifiedItems, setUnifiedItems] = useState<UnifiedHistoryItem[]>([]);
  const [cropItems, setCropItems] = useState<CropRecommendationHistoryItem[]>([]);
  const [diseaseItems, setDiseaseItems] = useState<DiseaseHistoryItem[]>([]);
  const [advisoryItems, setAdvisoryItems] = useState<AdvisoryConversationSummary[]>([]);

  // Detail Modal States
  const [selectedCrop, setSelectedCrop] = useState<CropRecommendationHistoryItem | null>(null);
  const [selectedDisease, setSelectedDisease] = useState<DiseaseHistoryItem | null>(null);
  const [selectedAdvisory, setSelectedAdvisory] = useState<AdvisoryConversationDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  // Fetch data based on active filter
  const fetchHistory = useCallback(async () => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      if (filter === 'all') {
        const summary = await historyService.getSummary(30);
        setUnifiedItems(summary.recent_activities || []);
      } else if (filter === 'crop') {
        const res = await historyService.getCropHistory(0, 50);
        setCropItems(res.items || []);
      } else if (filter === 'disease') {
        const res = await historyService.getDiseaseHistory(0, 50);
        setDiseaseItems(res.items || []);
      } else if (filter === 'queries') {
        const res = await historyService.getAdvisoryHistory(0, 50);
        setAdvisoryItems(res.items || []);
      }
    } catch (err: any) {
      const msg =
        err.response?.data?.detail ||
        err.message ||
        'Unable to load your farm history. Please try again.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, filter]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  // Open item detail
  const handleOpenDetail = async (type: 'crop' | 'disease' | 'advisory', id: string) => {
    setLoadingDetail(true);
    setDetailError(null);

    try {
      if (type === 'crop') {
        const detail = await historyService.getCropDetail(id);
        setSelectedCrop(detail);
      } else if (type === 'disease') {
        const detail = await historyService.getDiseaseDetail(id);
        setSelectedDisease(detail);
      } else if (type === 'advisory') {
        const detail = await historyService.getAdvisoryDetail(id);
        setSelectedAdvisory(detail);
      }
    } catch {
      setDetailError('Failed to load record details. Please try again.');
    } finally {
      setLoadingDetail(false);
    }
  };

  const closeModals = () => {
    setSelectedCrop(null);
    setSelectedDisease(null);
    setSelectedAdvisory(null);
    setDetailError(null);
  };

  const formatDate = (isoStr: string) => {
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString(undefined, {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoStr;
    }
  };

  // Unauthenticated Banner
  if (!isAuthenticated) {
    return (
      <div className="farmsathi-page-container" style={{ paddingTop: '2.5rem', paddingBottom: '5rem' }}>
        <PageHeader
          title={t.history.title || 'Farm History'}
          subtitle="Your recorded diagnoses, crop recommendations, and advisories."
          icon="history_edu"
        />
        <EmptyState
          icon="lock"
          title="Sign In to Access Farm History"
          description="Your personal crop recommendations, leaf disease scans, and FarmSathi advisory dialogues are securely tied to your farmer account."
          actionLabel="Sign In / Register"
          onAction={() => onOpenAuth?.()}
        />
      </div>
    );
  }

  // Filter items by search query
  const q = searchQuery.trim().toLowerCase();

  const filteredUnified = unifiedItems.filter((item) => {
    if (!q) return true;
    return (
      item.title.toLowerCase().includes(q) ||
      item.subtitle?.toLowerCase().includes(q) ||
      item.status?.toLowerCase().includes(q)
    );
  });

  const filteredCrops = cropItems.filter((item) => {
    if (!q) return true;
    return (
      item.recommended_crop.toLowerCase().includes(q) ||
      item.top_predictions.some((p) => p.crop.toLowerCase().includes(q))
    );
  });

  const filteredDiseases = diseaseItems.filter((item) => {
    if (!q) return true;
    return (
      item.crop.toLowerCase().includes(q) ||
      item.condition.toLowerCase().includes(q) ||
      item.display_name.toLowerCase().includes(q)
    );
  });

  const filteredAdvisories = advisoryItems.filter((item) => {
    if (!q) return true;
    return item.title.toLowerCase().includes(q);
  });

  return (
    <div className="farmsathi-page-container" style={{ paddingBottom: '6rem' }}>
      {/* Header and Controls */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '1.25rem' }}>
        <PageHeader
          title={t.history.title || 'Farm History'}
          subtitle={t.history.subtitle || 'Recent Farm Activity'}
          icon="history_edu"
        />

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', alignSelf: 'center' }}>
          <button
            type="button"
            aria-label="Search History"
            onClick={() => setShowSearch(!showSearch)}
            style={{
              width: '40px',
              height: '40px',
              borderRadius: 'var(--radius-full)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              color: 'var(--color-text-secondary)',
              cursor: 'pointer',
              transition: 'all var(--transition-fast)',
            }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
              {showSearch ? 'close' : 'search'}
            </span>
          </button>
        </div>
      </div>

      {showSearch && (
        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ position: 'relative' }}>
            <span
              className="material-symbols-outlined"
              style={{
                position: 'absolute',
                left: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--color-text-tertiary)',
                fontSize: '20px',
              }}
            >
              search
            </span>
            <input
              type="text"
              placeholder="Search past farm activities..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                height: '44px',
                padding: '0 1rem 0 2.5rem',
                borderRadius: 'var(--radius-md)',
                border: '1.5px solid var(--color-border)',
                backgroundColor: 'var(--color-surface)',
                fontSize: 'var(--font-size-sm)',
                color: 'var(--color-text-primary)',
                outline: 'none',
              }}
            />
          </div>
        </div>
      )}

      {/* Filter Tabs */}
      <nav
        aria-label="Filter records"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          overflowX: 'auto',
          paddingBottom: '0.5rem',
          marginBottom: '1.5rem',
        }}
      >
        {[
          { id: 'all', label: t.common.all || 'All Activity', icon: 'dashboard' },
          { id: 'disease', label: t.common.disease_detection || 'Disease Detection', icon: 'bug_report' },
          { id: 'crop', label: t.common.crop_recommendation || 'Crop Recommendation', icon: 'agriculture' },
          { id: 'queries', label: t.common.advisory || 'Advisory', icon: 'forum' },
        ].map((pill) => {
          const isActive = filter === pill.id;
          return (
            <button
              key={pill.id}
              type="button"
              onClick={() => setFilter(pill.id as any)}
              style={{
                whiteSpace: 'nowrap',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.5rem 1rem',
                borderRadius: 'var(--radius-full)',
                fontSize: 'var(--font-size-xs)',
                fontWeight: 600,
                backgroundColor: isActive ? 'var(--color-primary)' : 'var(--color-surface)',
                color: isActive ? 'var(--color-text-inverse)' : 'var(--color-text-secondary)',
                border: isActive ? '1px solid var(--color-primary)' : '1px solid var(--color-border)',
                boxShadow: isActive ? 'var(--shadow-sm)' : 'none',
                cursor: 'pointer',
                transition: 'all var(--transition-fast)',
              }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
                {pill.icon}
              </span>
              <span>{pill.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Main Content Feed */}
      <main style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* Loading State */}
        {loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <Skeleton height="88px" borderRadius="var(--radius-lg)" />
            <Skeleton height="88px" borderRadius="var(--radius-lg)" />
            <Skeleton height="88px" borderRadius="var(--radius-lg)" />
          </div>
        )}

        {/* Error State */}
        {!loading && error && (
          <Card surface="white" elevation="md" style={{ textAlign: 'center', padding: '2rem 1.5rem', border: '1px solid var(--color-error)' }}>
            <span className="material-symbols-outlined" style={{ fontSize: '36px', color: 'var(--color-error)' }}>
              error
            </span>
            <p style={{ marginTop: '0.5rem', fontSize: 'var(--font-size-sm)', color: 'var(--color-error)', fontWeight: 600 }}>
              {error}
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchHistory}
              style={{ marginTop: '1rem', display: 'inline-flex' }}
            >
              Retry
            </Button>
          </Card>
        )}

        {/* 1. All Activity Tab */}
        {!loading && !error && filter === 'all' && (
          <>
            {filteredUnified.length === 0 ? (
              <EmptyState
                icon="history_edu"
                title={t.common.no_activity || 'No Farm Activity Yet'}
                description={t.common.no_activity_desc || 'Your crop recommendations, disease scans, and farmer questions will show up here.'}
                actionLabel={t.common.ask_question || 'Ask Farm Question'}
                onAction={() => onNavigate?.('ask')}
                secondaryActionLabel={t.common.disease_detection || 'Scan Crop Leaf'}
                onSecondaryAction={() => onNavigate?.('diagnosis')}
              />
            ) : (
              filteredUnified.map((item) => {
                const icon =
                  item.module_type === 'crop'
                    ? 'agriculture'
                    : item.module_type === 'disease'
                      ? 'bug_report'
                      : 'chat';
                const badgeVariant =
                  item.status === 'Healthy'
                    ? 'success'
                    : item.status === 'Disease Detected'
                      ? 'error'
                      : 'neutral';

                return (
                  <Card
                    key={item.id}
                    hoverable
                    onClick={() => handleOpenDetail(item.module_type, item.id)}
                    style={{ cursor: 'pointer', padding: '1.25rem' }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.75rem' }}>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.85rem' }}>
                        <div
                          style={{
                            width: '42px',
                            height: '42px',
                            borderRadius: 'var(--radius-md)',
                            backgroundColor: 'var(--color-primary-light)',
                            color: 'var(--color-primary)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0,
                          }}
                        >
                          <span className="material-symbols-outlined" style={{ fontSize: '22px' }}>
                            {icon}
                          </span>
                        </div>
                        <div>
                          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)', marginBottom: '0.15rem' }}>
                            {formatDate(item.created_at)}
                          </div>
                          <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
                            {item.title}
                          </h3>
                          {item.subtitle && (
                            <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginTop: '0.2rem', margin: 0 }}>
                              {item.subtitle}
                            </p>
                          )}
                        </div>
                      </div>

                      {item.status && (
                        <Badge variant={badgeVariant as any} size="sm">
                          {item.status}
                        </Badge>
                      )}
                    </div>

                    <div
                      style={{
                        marginTop: '0.85rem',
                        paddingTop: '0.65rem',
                        borderTop: '1px solid var(--color-border-subtle)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        fontSize: 'var(--font-size-xs)',
                        fontWeight: 600,
                        color: 'var(--color-primary)',
                      }}
                    >
                      <span>
                        {item.module_type === 'advisory'
                          ? 'Open Dialogue'
                          : item.module_type === 'disease'
                            ? 'View Diagnosis & Remedies'
                            : 'View Recommendation Details'}
                      </span>
                      <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
                        arrow_forward
                      </span>
                    </div>
                  </Card>
                );
              })
            )}
          </>
        )}

        {/* 2. Crop Recommendation Tab */}
        {!loading && !error && filter === 'crop' && (
          <>
            {filteredCrops.length === 0 ? (
              <EmptyState
                icon="agriculture"
                title="No Crop Recommendations"
                description="Enter your soil N/P/K and weather details to receive tailored crop recommendations."
                actionLabel="Get Crop Recommendation"
                onAction={() => onNavigate?.('crops')}
              />
            ) : (
              filteredCrops.map((c) => (
                <Card
                  key={c.id}
                  hoverable
                  onClick={() => handleOpenDetail('crop', c.id)}
                  style={{ cursor: 'pointer', padding: '1.25rem' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.65rem' }}>
                    <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)' }}>
                      {formatDate(c.created_at)}
                    </span>
                    <Badge variant="primary" size="sm">
                      {c.recommended_crop.toUpperCase()}
                    </Badge>
                  </div>

                  <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--color-text-primary)', margin: '0 0 0.5rem 0' }}>
                    Recommended: {c.recommended_crop.charAt(0).toUpperCase() + c.recommended_crop.slice(1)}
                  </h3>

                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(4, 1fr)',
                      gap: '0.4rem',
                      backgroundColor: 'var(--color-surface-sunken)',
                      padding: '0.5rem',
                      borderRadius: 'var(--radius-md)',
                      fontSize: 'var(--font-size-xs)',
                      textAlign: 'center',
                    }}
                  >
                    <div>
                      <span style={{ display: 'block', color: 'var(--color-text-tertiary)', fontSize: '11px', fontWeight: 600 }}>N</span>
                      <strong>{c.inputs.N?.toFixed(0)}</strong>
                    </div>
                    <div>
                      <span style={{ display: 'block', color: 'var(--color-text-tertiary)', fontSize: '11px', fontWeight: 600 }}>P</span>
                      <strong>{c.inputs.P?.toFixed(0)}</strong>
                    </div>
                    <div>
                      <span style={{ display: 'block', color: 'var(--color-text-tertiary)', fontSize: '11px', fontWeight: 600 }}>K</span>
                      <strong>{c.inputs.K?.toFixed(0)}</strong>
                    </div>
                    <div>
                      <span style={{ display: 'block', color: 'var(--color-text-tertiary)', fontSize: '11px', fontWeight: 600 }}>pH</span>
                      <strong>{c.inputs.ph?.toFixed(1)}</strong>
                    </div>
                  </div>

                  <div
                    style={{
                      marginTop: '0.85rem',
                      paddingTop: '0.65rem',
                      borderTop: '1px solid var(--color-border-subtle)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      fontSize: 'var(--font-size-xs)',
                      fontWeight: 600,
                      color: 'var(--color-primary)',
                    }}
                  >
                    <span>View Recommendation Details</span>
                    <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
                      arrow_forward
                    </span>
                  </div>
                </Card>
              ))
            )}
          </>
        )}

        {/* 3. Disease Diagnosis Tab */}
        {!loading && !error && filter === 'disease' && (
          <>
            {filteredDiseases.length === 0 ? (
              <EmptyState
                icon="bug_report"
                title="No Disease Diagnoses"
                description="Upload a photo of your crop leaf for automated disease identification and organic remedies."
                actionLabel="Scan Crop Leaf"
                onAction={() => onNavigate?.('diagnosis')}
              />
            ) : (
              filteredDiseases.map((d) => (
                <Card
                  key={d.id}
                  hoverable
                  onClick={() => handleOpenDetail('disease', d.id)}
                  style={{ cursor: 'pointer', padding: '1.25rem' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.65rem' }}>
                    <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)' }}>
                      {formatDate(d.created_at)}
                    </span>
                    <Badge variant={d.is_healthy ? 'success' : 'error'} size="sm">
                      {d.is_healthy ? 'Healthy' : `${(d.confidence * 100).toFixed(0)}% Match`}
                    </Badge>
                  </div>

                  <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
                    {d.crop}: {d.display_name}
                  </h3>
                  <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginTop: '0.25rem', margin: 0 }}>
                    Condition: <strong>{d.condition}</strong>
                  </p>

                  <div
                    style={{
                      marginTop: '0.85rem',
                      paddingTop: '0.65rem',
                      borderTop: '1px solid var(--color-border-subtle)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      fontSize: 'var(--font-size-xs)',
                      fontWeight: 600,
                      color: 'var(--color-primary)',
                    }}
                  >
                    <span>View Full Diagnosis & Guidance</span>
                    <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
                      arrow_forward
                    </span>
                  </div>
                </Card>
              ))
            )}
          </>
        )}

        {/* 4. Advisory Conversations Tab */}
        {!loading && !error && filter === 'queries' && (
          <>
            {filteredAdvisories.length === 0 ? (
              <EmptyState
                icon="forum"
                title="No Advisory Conversations"
                description="Ask questions in your preferred language using voice or text."
                actionLabel="Start New Conversation"
                onAction={() => onNavigate?.('ask')}
              />
            ) : (
              filteredAdvisories.map((a) => (
                <Card
                  key={a.id}
                  hoverable
                  onClick={() => handleOpenDetail('advisory', a.id)}
                  style={{ cursor: 'pointer', padding: '1.25rem' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)' }}>
                      {formatDate(a.updated_at || a.created_at)}
                    </span>
                    <Badge variant="neutral" size="sm">
                      {a.language.toUpperCase()}
                    </Badge>
                  </div>

                  <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--color-text-primary)', margin: 0 }}>
                    {a.title}
                  </h3>
                  <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginTop: '0.25rem', display: 'block' }}>
                    {a.message_count} message{a.message_count !== 1 ? 's' : ''} in dialogue
                  </span>

                  <div
                    style={{
                      marginTop: '0.85rem',
                      paddingTop: '0.65rem',
                      borderTop: '1px solid var(--color-border-subtle)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      fontSize: 'var(--font-size-xs)',
                      fontWeight: 600,
                      color: 'var(--color-primary)',
                    }}
                  >
                    <span>Open Conversation</span>
                    <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
                      arrow_forward
                    </span>
                  </div>
                </Card>
              ))
            )}
          </>
        )}
      </main>

      {/* DETAIL MODAL: CROP RECOMMENDATION */}
      <Modal
        isOpen={Boolean(selectedCrop)}
        onClose={closeModals}
        title="Crop Recommendation Details"
      >
        {selectedCrop && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div
              style={{
                backgroundColor: 'var(--color-primary-light)',
                borderRadius: 'var(--radius-lg)',
                padding: '1.25rem',
                textAlign: 'center',
              }}
            >
              <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-primary)', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 700 }}>
                Top Recommendation
              </span>
              <h2 style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 800, color: 'var(--color-primary)', margin: '0.25rem 0' }}>
                {selectedCrop.recommended_crop.toUpperCase()}
              </h2>
              <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>
                Recorded on {formatDate(selectedCrop.created_at)}
              </span>
            </div>

            <div>
              <h4 style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, margin: '0 0 0.5rem 0' }}>
                Top Prediction Matches:
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                {selectedCrop.top_predictions.map((p, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      padding: '0.5rem 0.75rem',
                      backgroundColor: 'var(--color-surface-sunken)',
                      borderRadius: 'var(--radius-md)',
                      fontSize: 'var(--font-size-xs)',
                    }}
                  >
                    <span style={{ fontWeight: 600 }}>{p.crop.charAt(0).toUpperCase() + p.crop.slice(1)}</span>
                    <span style={{ color: 'var(--color-primary)', fontWeight: 700 }}>{(p.probability * 100).toFixed(1)}% match</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, margin: '0 0 0.5rem 0' }}>
                Soil & Weather Inputs Evaluated:
              </h4>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '0.5rem',
                  backgroundColor: 'var(--color-surface-sunken)',
                  padding: '0.75rem',
                  borderRadius: 'var(--radius-md)',
                  fontSize: 'var(--font-size-xs)',
                }}
              >
                <div>Nitrogen (N): <strong>{selectedCrop.inputs.N}</strong></div>
                <div>Phosphorus (P): <strong>{selectedCrop.inputs.P}</strong></div>
                <div>Potassium (K): <strong>{selectedCrop.inputs.K}</strong></div>
                <div>Soil pH: <strong>{selectedCrop.inputs.ph}</strong></div>
                <div>Temperature: <strong>{selectedCrop.inputs.temperature}°C</strong></div>
                <div>Humidity: <strong>{selectedCrop.inputs.humidity}%</strong></div>
                <div>Rainfall: <strong>{selectedCrop.inputs.rainfall} mm</strong></div>
                <div>Model Version: <strong>{selectedCrop.model_version}</strong></div>
              </div>
            </div>

            <Button variant="primary" fullWidth onClick={closeModals} style={{ marginTop: '0.5rem' }}>
              Close
            </Button>
          </div>
        )}
      </Modal>

      {/* DETAIL MODAL: DISEASE DIAGNOSIS */}
      <Modal
        isOpen={Boolean(selectedDisease)}
        onClose={closeModals}
        title="Disease Diagnosis Details"
      >
        {selectedDisease && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {selectedDisease.image_url && (
              <div style={{ borderRadius: 'var(--radius-lg)', overflow: 'hidden', textAlign: 'center', backgroundColor: 'var(--color-header-bg, #354024)', maxHeight: '200px' }}>
                <img
                  src={selectedDisease.image_url}
                  alt={selectedDisease.display_name}
                  style={{ maxHeight: '200px', width: 'auto', margin: '0 auto', display: 'block' }}
                  onError={(e) => {
                    (e.target as HTMLElement).style.display = 'none';
                  }}
                />
              </div>
            )}

            <div
              style={{
                backgroundColor: selectedDisease.is_healthy ? 'var(--color-success-bg)' : 'rgba(211, 47, 47, 0.08)',
                borderRadius: 'var(--radius-lg)',
                padding: '1rem',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h4 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: selectedDisease.is_healthy ? 'var(--color-success)' : 'var(--color-error)', margin: 0 }}>
                  {selectedDisease.crop}: {selectedDisease.display_name}
                </h4>
                <Badge variant={selectedDisease.is_healthy ? 'success' : 'error'} size="sm">
                  {(selectedDisease.confidence * 100).toFixed(1)}% Match
                </Badge>
              </div>
              <p style={{ fontSize: 'var(--font-size-xs)', marginTop: '0.25rem', color: 'var(--color-text-secondary)', margin: '0.25rem 0 0 0' }}>
                Diagnosed on {formatDate(selectedDisease.created_at)}
              </p>
            </div>

            {selectedDisease.management_guidance && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: 'var(--font-size-xs)' }}>
                {selectedDisease.management_guidance.cultural_practices?.length > 0 && (
                  <div>
                    <strong style={{ display: 'block', marginBottom: '0.25rem', color: 'var(--color-text-primary)' }}>
                      Cultural Practices:
                    </strong>
                    <ul style={{ paddingLeft: '1.25rem', margin: 0 }}>
                      {selectedDisease.management_guidance.cultural_practices.map((item: string, i: number) => (
                        <li key={i} style={{ marginBottom: '0.2rem' }}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {selectedDisease.management_guidance.sanitation?.length > 0 && (
                  <div>
                    <strong style={{ display: 'block', marginBottom: '0.25rem', color: 'var(--color-text-primary)' }}>
                      Sanitation:
                    </strong>
                    <ul style={{ paddingLeft: '1.25rem', margin: 0 }}>
                      {selectedDisease.management_guidance.sanitation.map((item: string, i: number) => (
                        <li key={i} style={{ marginBottom: '0.2rem' }}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {selectedDisease.management_guidance.prevention?.length > 0 && (
                  <div>
                    <strong style={{ display: 'block', marginBottom: '0.25rem', color: 'var(--color-text-primary)' }}>
                      Prevention:
                    </strong>
                    <ul style={{ paddingLeft: '1.25rem', margin: 0 }}>
                      {selectedDisease.management_guidance.prevention.map((item: string, i: number) => (
                        <li key={i} style={{ marginBottom: '0.2rem' }}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {selectedDisease.management_guidance.disclaimer && (
                  <p style={{ fontStyle: 'italic', color: 'var(--color-text-tertiary)', borderLeft: '3px solid var(--color-border)', paddingLeft: '0.5rem', marginTop: '0.5rem', margin: 0 }}>
                    {selectedDisease.management_guidance.disclaimer}
                  </p>
                )}
              </div>
            )}

            <Button variant="primary" fullWidth onClick={closeModals} style={{ marginTop: '0.5rem' }}>
              Close
            </Button>
          </div>
        )}
      </Modal>

      {/* DETAIL MODAL: ADVISORY CONVERSATION */}
      <Modal
        isOpen={Boolean(selectedAdvisory)}
        onClose={closeModals}
        title={selectedAdvisory?.title || 'Advisory Conversation'}
      >
        {selectedAdvisory && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxHeight: '70vh' }}>
            <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem', paddingRight: '0.25rem' }}>
              {selectedAdvisory.messages.map((m) => {
                const isUser = m.sender_role === 'user';
                return (
                  <div
                    key={m.id}
                    style={{
                      alignSelf: isUser ? 'flex-end' : 'flex-start',
                      maxWidth: '85%',
                      backgroundColor: isUser ? 'var(--color-primary)' : 'var(--color-surface-sunken)',
                      color: isUser ? 'var(--color-text-inverse)' : 'var(--color-text-primary)',
                      borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                      padding: '0.75rem 1rem',
                      fontSize: 'var(--font-size-xs)',
                      lineHeight: 1.5,
                      boxShadow: 'var(--shadow-xs)',
                    }}
                  >
                    <div style={{ fontWeight: 700, marginBottom: '0.2rem', opacity: 0.85 }}>
                      {isUser ? 'You (Farmer)' : 'FarmSathi Advisory'}
                    </div>
                    <div>{m.message_text}</div>
                    <span style={{ display: 'block', fontSize: '10px', marginTop: '0.35rem', opacity: 0.75, textAlign: 'right' }}>
                      {formatDate(m.created_at)}
                    </span>
                  </div>
                );
              })}
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
              <Button
                variant="primary"
                fullWidth
                onClick={() => {
                  const convId = selectedAdvisory.id;
                  closeModals();
                  if (onNavigate) onNavigate('ask', undefined, convId);
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                  forum
                </span>
                <span>Continue Chat in Advisory</span>
              </Button>
              <Button variant="outline" onClick={closeModals}>
                Close
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Detail Loading Overlay */}
      {loadingDetail && (
        <div
          role="status"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.4)',
            backdropFilter: 'blur(3px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1100,
          }}
        >
          <Card surface="white" elevation="md" style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1.25rem 2rem' }}>
            <span
              className="material-symbols-outlined"
              style={{
                fontSize: '28px',
                color: 'var(--color-primary)',
                animation: 'spin 1.2s linear infinite',
              }}
            >
              progress_activity
            </span>
            <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
              Loading record details...
            </span>
          </Card>
        </div>
      )}

      {/* Detail Error Toast */}
      {detailError && (
        <div
          role="alert"
          style={{
            position: 'fixed',
            bottom: '5rem',
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: 'var(--color-error)',
            color: 'var(--color-text-inverse, #E5D7C4)',
            padding: '0.75rem 1.5rem',
            borderRadius: 'var(--radius-full)',
            fontSize: 'var(--font-size-xs)',
            fontWeight: 600,
            boxShadow: 'var(--shadow-md)',
            zIndex: 1200,
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <span>{detailError}</span>
          <button type="button" onClick={() => setDetailError(null)} style={{ color: 'var(--color-text-inverse, #E5D7C4)', background: 'none', border: 'none', cursor: 'pointer', display: 'flex' }}>
            <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>close</span>
          </button>
        </div>
      )}
    </div>
  );
};
