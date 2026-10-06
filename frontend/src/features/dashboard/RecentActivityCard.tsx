import React from 'react';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Clock, Sprout, ScanLine, ArrowUpRight } from 'lucide-react';

interface RecentActivityCardProps {
  onViewHistory: () => void;
}

export const RecentActivityCard: React.FC<RecentActivityCardProps> = ({ onViewHistory }) => {
  return (
    <Card>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
          <Clock size={18} color="var(--color-primary)" />
          <h4 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--color-text-primary)' }}>
            Recent Activity & Insights
          </h4>
        </div>
        <button
          onClick={onViewHistory}
          style={{
            fontSize: 'var(--font-size-xs)',
            fontWeight: 700,
            color: 'var(--color-primary)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.2rem',
          }}
        >
          <span>View All</span>
          <ArrowUpRight size={14} />
        </button>
      </div>

      {/* Activity item examples adhering to Stitch designs */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0.75rem',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--color-surface-hover)',
            border: '1px solid var(--color-border)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div
              style={{
                backgroundColor: 'var(--color-primary-surface)',
                color: 'var(--color-primary)',
                padding: '0.5rem',
                borderRadius: 'var(--radius-md)',
                display: 'flex',
              }}
            >
              <Sprout size={18} />
            </div>
            <div>
              <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                Crop Suitability Run
              </div>
              <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
                Ready to test your soil parameters
              </div>
            </div>
          </div>
          <Badge variant="primary" size="sm">
            Ready
          </Badge>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0.75rem',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--color-surface-hover)',
            border: '1px solid var(--color-border)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div
              style={{
                backgroundColor: 'var(--color-harvest-light)',
                color: 'var(--color-harvest)',
                padding: '0.5rem',
                borderRadius: 'var(--radius-md)',
                display: 'flex',
              }}
            >
              <ScanLine size={18} />
            </div>
            <div>
              <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                Plant Health Scanner
              </div>
              <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
                Upload a leaf photo to diagnose condition
              </div>
            </div>
          </div>
          <Badge variant="neutral" size="sm">
            Standby
          </Badge>
        </div>
      </div>
    </Card>
  );
};
