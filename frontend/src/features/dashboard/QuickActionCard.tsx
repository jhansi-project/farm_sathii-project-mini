import React from 'react';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { ChevronRight } from 'lucide-react';

interface QuickActionCardProps {
  title: string;
  description: string;
  badgeText?: string;
  icon: React.ReactNode;
  iconBgColor?: string;
  onClick: () => void;
}

export const QuickActionCard: React.FC<QuickActionCardProps> = ({
  title,
  description,
  badgeText,
  icon,
  iconBgColor = 'var(--color-primary-surface)',
  onClick,
}) => {
  return (
    <Card
      hoverable
      onClick={onClick}
      style={{
        cursor: 'pointer',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        minHeight: '135px',
        border: '1.5px solid var(--color-border)',
      }}
    >
      <div>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
          <div
            style={{
              backgroundColor: iconBgColor,
              color: 'var(--color-primary)',
              borderRadius: 'var(--radius-md)',
              padding: '0.65rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </div>
          {badgeText && (
            <Badge variant="primary" size="sm">
              {badgeText}
            </Badge>
          )}
        </div>
        <h4 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--color-text-primary)', marginBottom: '0.25rem' }}>
          {title}
        </h4>
        <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)', lineHeight: 1.4 }}>
          {description}
        </p>
      </div>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.2rem',
          fontSize: 'var(--font-size-xs)',
          fontWeight: 700,
          color: 'var(--color-primary)',
          marginTop: '0.75rem',
        }}
      >
        <span>Open</span>
        <ChevronRight size={14} />
      </div>
    </Card>
  );
};
