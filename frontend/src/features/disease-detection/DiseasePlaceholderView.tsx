import React from 'react';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Camera } from 'lucide-react';

export const DiseasePlaceholderView: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--color-primary)' }}>
            Plant Disease Diagnostic Scanner
          </h2>
          <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
            Computer vision leaf diagnosis trained on Indian crop pathologies
          </p>
        </div>
        <Badge variant="warning">Phase 6 Pipeline</Badge>
      </div>

      <Card style={{ textAlign: 'center', padding: '2.5rem 1.5rem' }}>
        <div
          style={{
            width: '64px',
            height: '64px',
            borderRadius: 'var(--radius-full)',
            backgroundColor: 'var(--color-harvest-light)',
            color: 'var(--color-harvest)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1rem auto',
          }}
        >
          <Camera size={32} />
        </div>
        <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, marginBottom: '0.5rem' }}>
          Camera Capture & Leaf Image Upload
        </h3>
        <p style={{ maxWidth: '480px', margin: '0 auto', fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
          In Phase 6, you will be able to take a live photo using your phone camera or upload a saved leaf picture to detect plant diseases with confidence thresholding and preventive care guidance.
        </p>
      </Card>
    </div>
  );
};
