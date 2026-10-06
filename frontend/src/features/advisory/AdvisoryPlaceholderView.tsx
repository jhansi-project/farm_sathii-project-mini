import React from 'react';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { MessageSquare } from 'lucide-react';

export const AdvisoryPlaceholderView: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--color-primary)' }}>
            FarmSathi Natural-Language Advisory
          </h2>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
            Ask agricultural questions by voice or text with context-aware guidance
          </p>
        </div>
        <Badge variant="primary">Phase 7 & 9</Badge>
      </div>

      <Card style={{ textAlign: 'center', padding: '2.5rem 1.5rem' }}>
        <div
          style={{
            width: '64px',
            height: '64px',
            borderRadius: 'var(--radius-full)',
            backgroundColor: 'var(--color-primary-surface)',
            color: 'var(--color-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1rem auto',
          }}
        >
          <MessageSquare size={32} />
        </div>
        <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, marginBottom: '0.5rem' }}>
          Conversational Agronomy Support
        </h3>
        <p style={{ maxWidth: '480px', margin: '0 auto', fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
          In Phase 7, you will be able to ask natural-language questions such as: "Yesterday morning I applied fertilizer and today the leaves are curling. What should I do?" and receive contextual, verified agricultural guidance.
        </p>
      </Card>
    </div>
  );
};
