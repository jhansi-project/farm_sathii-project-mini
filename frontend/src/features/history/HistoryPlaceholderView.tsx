import React from 'react';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { History } from 'lucide-react';

export const HistoryPlaceholderView: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--color-primary)' }}>
            Historical Farm Records
          </h2>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
            Past crop recommendations, disease scan logs, and advisory transcripts
          </p>
        </div>
        <Badge variant="neutral">Phase 10</Badge>
      </div>

      <Card style={{ textAlign: 'center', padding: '2.5rem 1.5rem' }}>
        <div
          style={{
            width: '64px',
            height: '64px',
            borderRadius: 'var(--radius-full)',
            backgroundColor: 'var(--color-surface-hover)',
            color: 'var(--color-text-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1rem auto',
          }}
        >
          <History size={32} />
        </div>
        <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, marginBottom: '0.5rem' }}>
          Interactive Historical Timeline
        </h3>
        <p style={{ maxWidth: '480px', margin: '0 auto', fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
          In Phase 10, all previous diagnoses, recommendations, and chats persisted in PostgreSQL 18 will be accessible with filtering and deep-dive detail cards.
        </p>
      </Card>
    </div>
  );
};
