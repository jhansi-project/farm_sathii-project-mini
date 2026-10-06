import React from 'react';
import { Spinner } from './Spinner';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'subtle' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  fullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  fullWidth = false,
  leftIcon,
  rightIcon,
  disabled,
  style,
  ...props
}) => {
  const getVariantStyles = (): React.CSSProperties => {
    switch (variant) {
      case 'secondary':
        return {
          backgroundColor: 'var(--color-secondary)',
          color: 'var(--color-text-inverse)',
          border: '1px solid var(--color-secondary)',
          boxShadow: 'var(--shadow-xs)',
        };
      case 'outline':
        return {
          backgroundColor: 'var(--color-surface)',
          color: 'var(--color-primary)',
          border: '1.5px solid var(--color-primary)',
          boxShadow: 'var(--shadow-xs)',
        };
      case 'subtle':
        return {
          backgroundColor: 'var(--color-surface-container)',
          color: 'var(--color-primary)',
          border: '1px solid var(--color-border)',
        };
      case 'ghost':
        return {
          backgroundColor: 'transparent',
          color: 'var(--color-text-primary)',
          border: 'none',
        };
      case 'danger':
        return {
          backgroundColor: 'var(--color-primary)',
          color: 'var(--color-text-inverse)',
          border: 'none',
          boxShadow: 'var(--shadow-xs)',
        };
      case 'primary':
      default:
        return {
          backgroundColor: 'var(--color-primary)',
          color: 'var(--color-text-inverse)',
          border: 'none',
          boxShadow: 'var(--shadow-sm)',
        };
    }
  };

  const getSizeStyles = (): React.CSSProperties => {
    switch (size) {
      case 'sm':
        return {
          padding: '0.4rem 0.85rem',
          fontSize: 'var(--font-size-xs)',
          minHeight: '38px',
          borderRadius: 'var(--radius-md)',
        };
      case 'lg':
        return {
          padding: '0.85rem 1.75rem',
          fontSize: 'var(--font-size-base)',
          minHeight: '52px',
          borderRadius: 'var(--radius-lg)',
        };
      case 'md':
      default:
        return {
          padding: '0.65rem 1.25rem',
          fontSize: 'var(--font-size-sm)',
          minHeight: '44px',
          borderRadius: 'var(--radius-md)',
        };
    }
  };

  const isInteractive = !disabled && !isLoading;

  return (
    <button
      disabled={disabled || isLoading}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        fontFamily: 'var(--font-primary)',
        fontWeight: 600,
        letterSpacing: '-0.01em',
        transition: 'all var(--transition-fast)',
        cursor: isInteractive ? 'pointer' : 'not-allowed',
        opacity: disabled ? 0.6 : 1,
        width: fullWidth ? '100%' : 'auto',
        ...getVariantStyles(),
        ...getSizeStyles(),
        ...style,
      }}
      onMouseEnter={(e) => {
        if (isInteractive) {
          if (variant === 'primary') {
            e.currentTarget.style.backgroundColor = 'var(--color-primary-hover)';
            e.currentTarget.style.boxShadow = 'var(--shadow-md)';
          } else if (variant === 'outline') {
            e.currentTarget.style.backgroundColor = 'var(--color-primary-light)';
          } else if (variant === 'secondary') {
            e.currentTarget.style.backgroundColor = 'var(--color-secondary-hover)';
          } else if (variant === 'ghost') {
            e.currentTarget.style.backgroundColor = 'rgba(76, 61, 25, 0.08)';
          }
        }
        props.onMouseEnter?.(e);
      }}
      onMouseLeave={(e) => {
        if (isInteractive) {
          const defaultStyles = getVariantStyles();
          e.currentTarget.style.backgroundColor = String(defaultStyles.backgroundColor);
          e.currentTarget.style.boxShadow = defaultStyles.boxShadow ? String(defaultStyles.boxShadow) : 'none';
        }
        props.onMouseLeave?.(e);
      }}
      onMouseDown={(e) => {
        if (isInteractive) {
          e.currentTarget.style.transform = 'scale(0.98)';
        }
        props.onMouseDown?.(e);
      }}
      onMouseUp={(e) => {
        if (isInteractive) {
          e.currentTarget.style.transform = 'scale(1)';
        }
        props.onMouseUp?.(e);
      }}
      {...props}
    >
      {isLoading ? (
        <Spinner size={size === 'sm' ? 'sm' : 'md'} />
      ) : (
        <>
          {leftIcon && <span style={{ display: 'inline-flex', alignItems: 'center' }}>{leftIcon}</span>}
          <span>{children}</span>
          {rightIcon && <span style={{ display: 'inline-flex', alignItems: 'center' }}>{rightIcon}</span>}
        </>
      )}
    </button>
  );
};

