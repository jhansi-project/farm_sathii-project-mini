import React from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { useAuthStore } from '../../stores/authStore';
import { Sprout, MapPin, Layers, Droplet } from 'lucide-react';

interface FarmSummaryCardProps {
  onOpenProfile: () => void;
  onOpenAuth: () => void;
}

export const FarmSummaryCard: React.FC<FarmSummaryCardProps> = ({ onOpenProfile, onOpenAuth }) => {
  const { user, isAuthenticated } = useAuthStore();
  const profile = user?.profile;

  if (!isAuthenticated || !user) {
    return (
      <Card
        style={{
          border: '1.5px dashed var(--color-border)',
          backgroundColor: 'var(--color-surface-hover)',
          textAlign: 'center',
          padding: '1.5rem',
        }}
      >
        <Sprout size={32} color="var(--color-primary)" style={{ margin: '0 auto 0.5rem auto' }} />
        <h4 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, marginBottom: '0.25rem' }}>
          Personalize Your Farm Insights
        </h4>
        <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', marginBottom: '1rem' }}>
          Sign in to save your soil test records, crop recommendations, and diagnosis history.
        </p>
        <Button size="sm" onClick={onOpenAuth}>
          Sign In / Register
        </Button>
      </Card>
    );
  }

  return (
    <Card>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
        <h4 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--color-text-primary)' }}>
          My Farm Profile
        </h4>
        <Button size="sm" variant="ghost" onClick={onOpenProfile} style={{ padding: '0.2rem 0.5rem', minHeight: '32px' }}>
          Edit Details
        </Button>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
          gap: '0.75rem',
        }}
      >
        <div style={{ padding: '0.65rem', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--color-primary-surface)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--color-text-muted)', fontSize: 'var(--font-size-xs)' }}>
            <Layers size={14} />
            <span>Soil Type</span>
          </div>
          <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--color-primary)', marginTop: '0.2rem' }}>
            {profile?.soil_type || 'Loamy Soil'}
          </div>
        </div>

        <div style={{ padding: '0.65rem', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--color-primary-surface)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--color-text-muted)', fontSize: 'var(--font-size-xs)' }}>
            <Sprout size={14} />
            <span>Land Size</span>
          </div>
          <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--color-primary)', marginTop: '0.2rem' }}>
            {profile?.land_size_acres ? `${profile.land_size_acres} Acres` : 'Not set'}
          </div>
        </div>

        <div style={{ padding: '0.65rem', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--color-primary-surface)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--color-text-muted)', fontSize: 'var(--font-size-xs)' }}>
            <MapPin size={14} />
            <span>Location</span>
          </div>
          <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--color-primary)', marginTop: '0.2rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {profile?.district ? `${profile.district}, ${profile.state || ''}` : 'Location pending'}
          </div>
        </div>

        <div style={{ padding: '0.65rem', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--color-primary-surface)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--color-text-muted)', fontSize: 'var(--font-size-xs)' }}>
            <Droplet size={14} />
            <span>Irrigation</span>
          </div>
          <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: 700, color: 'var(--color-primary)', marginTop: '0.2rem' }}>
            {profile?.irrigation_source || 'Canal'}
          </div>
        </div>
      </div>
    </Card>
  );
};
