import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hoverable?: boolean;
  padding?: 'none' | 'xs' | 'sm' | 'md' | 'lg';
  borderVariant?: 'default' | 'primary' | 'subtle' | 'none';
  elevation?: 'none' | 'xs' | 'sm' | 'md';
  surface?: 'white' | 'subtle' | 'container';
}

export const Card: React.FC<CardProps> = ({
  children,
  hoverable = false,
  padding = 'md',
  borderVariant = 'default',
  elevation = 'xs',
  surface = 'white',
  style,
  className,
  ...props
}) => {
  const getPadding = () => {
    switch (padding) {
      case 'none':
        return 0;
      case 'xs':
        return '0.5rem';
      case 'sm':
        return '0.85rem';
      case 'lg':
        return '1.5rem 1.75rem';
      case 'md':
      default:
        return '1.25rem';
    }
  };

  const getBorder = () => {
    switch (borderVariant) {
      case 'none':
        return 'none';
      case 'primary':
        return '1px solid var(--color-primary-subtle)';
      case 'subtle':
        return '1px solid var(--color-border-subtle)';
      case 'default':
      default:
        return '1px solid var(--color-border)';
    }
  };

  const getBackground = () => {
    switch (surface) {
      case 'subtle':
        return 'var(--color-surface-container-low)';
      case 'container':
        return 'var(--color-surface-container)';
      case 'white':
      default:
        return 'var(--color-surface)';
    }
  };

  const getShadow = () => {
    switch (elevation) {
      case 'none':
        return 'none';
      case 'sm':
        return 'var(--shadow-sm)';
      case 'md':
        return 'var(--shadow-md)';
      case 'xs':
      default:
        return 'var(--shadow-xs)';
    }
  };

  const isInteractive = hoverable || Boolean(props.onClick);

  return (
    <div
      style={{
        backgroundColor: getBackground(),
        border: getBorder(),
        borderRadius: 'var(--radius-xl)',
        boxShadow: getShadow(),
        padding: getPadding(),
        transition: isInteractive
          ? 'transform var(--transition-fast), box-shadow var(--transition-fast), border-color var(--transition-fast)'
          : undefined,
        cursor: isInteractive ? 'pointer' : undefined,
        ...style,
      }}
      onMouseEnter={(e) => {
        if (isInteractive) {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = 'var(--shadow-md)';
          e.currentTarget.style.borderColor = 'var(--color-primary-subtle)';
        }
        props.onMouseEnter?.(e);
      }}
      onMouseLeave={(e) => {
        if (isInteractive) {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = getShadow();
          const borderVal = getBorder();
          e.currentTarget.style.borderColor =
            borderVal === 'none' ? 'transparent' : borderVal.replace('1px solid ', '');
        }
        props.onMouseLeave?.(e);
      }}
      {...props}
    >
      {children}
    </div>
  );
};

