import React from 'react';

export interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info' | 'warning';
  onClose?: () => void;
}

export const Toast: React.FC<ToastProps> = ({ message, type = 'info', onClose }) => {
  const getIconName = () => {
    switch (type) {
      case 'success':
        return 'check_circle';
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
      default:
        return 'info';
    }
  };

  const getStyles = () => {
    switch (type) {
      case 'success':
        return {
          bg: 'var(--color-success-bg)',
          border: 'var(--color-success-border)',
          color: 'var(--color-success)',
        };
      case 'error':
        return {
          bg: 'var(--color-error-bg)',
          border: 'var(--color-error-border)',
          color: 'var(--color-error)',
        };
      case 'warning':
        return {
          bg: 'var(--color-warning-bg)',
          border: 'var(--color-warning-border)',
          color: 'var(--color-warning)',
        };
      case 'info':
      default:
        return {
          bg: 'var(--color-info-bg)',
          border: 'var(--color-info-border)',
          color: 'var(--color-info)',
        };
    }
  };

  const currentStyles = getStyles();

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0.75rem 1rem',
        borderRadius: 'var(--radius-lg)',
        backgroundColor: currentStyles.bg,
        border: `1px solid ${currentStyles.border}`,
        boxShadow: 'var(--shadow-md)',
        fontSize: 'var(--font-size-sm)',
        fontWeight: 500,
        gap: '0.75rem',
        color: 'var(--color-on-surface)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
        <span
          className="material-symbols-outlined"
          style={{
            fontSize: '20px',
            color: currentStyles.color,
            fontVariationSettings: "'FILL' 1",
          }}
        >
          {getIconName()}
        </span>
        <span>{message}</span>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          type="button"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--color-text-muted)',
            cursor: 'pointer',
          }}
          aria-label="Close notification"
        >
          <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
            close
          </span>
        </button>
      )}
    </div>
  );
};

