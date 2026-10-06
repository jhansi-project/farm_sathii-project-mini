import React from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'primary' | 'success' | 'warning' | 'error' | 'info' | 'neutral';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  style,
  ...props
}) => {
  const getVariantStyles = (): React.CSSProperties => {
    switch (variant) {
      case 'primary':
        return {
          backgroundColor: 'var(--color-primary-light)',
          color: 'var(--color-primary)',
          border: '1px solid var(--color-primary-subtle)',
        };
      case 'success':
        return {
          backgroundColor: 'var(--color-success-bg)',
          color: 'var(--color-success)',
          border: '1px solid var(--color-success-border)',
        };
      case 'warning':
        return {
          backgroundColor: 'var(--color-warning-bg)',
          color: 'var(--color-warning)',
          border: '1px solid var(--color-warning-border)',
        };
      case 'error':
        return {
          backgroundColor: 'var(--color-error-bg)',
          color: 'var(--color-error)',
          border: '1px solid var(--color-error-border)',
        };
      case 'info':
        return {
          backgroundColor: 'var(--color-info-bg)',
          color: 'var(--color-info)',
          border: '1px solid var(--color-info-border)',
        };
      case 'neutral':
      default:
        return {
          backgroundColor: 'var(--color-surface-container-low)',
          color: 'var(--color-on-surface-variant)',
          border: '1px solid var(--color-border)',
        };
    }
  };

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.35rem',
        borderRadius: 'var(--radius-full)',
        fontFamily: 'var(--font-primary)',
        fontWeight: 600,
        padding: size === 'sm' ? '0.2rem 0.55rem' : '0.3rem 0.75rem',
        fontSize: size === 'sm' ? 'var(--font-size-xs)' : '13px',
        lineHeight: 1,
        letterSpacing: '0.01em',
        ...getVariantStyles(),
        ...style,
      }}
      {...props}
    >
      {children}
    </span>
  );
};

