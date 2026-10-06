import React, { forwardRef, useState } from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, leftIcon, rightIcon, style, id, onFocus, onBlur, ...props }, ref) => {
    const [isFocused, setIsFocused] = useState(false);
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(true);
      onFocus?.(e);
    };

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(false);
      onBlur?.(e);
    };

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', width: '100%' }}>
        {label && (
          <label
            htmlFor={inputId}
            style={{
              fontSize: 'var(--font-size-sm)',
              fontWeight: 600,
              color: 'var(--color-text-primary)',
              letterSpacing: '-0.01em',
            }}
          >
            {label}
          </label>
        )}
        <div
          style={{
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            width: '100%',
          }}
        >
          {leftIcon && (
            <span
              style={{
                position: 'absolute',
                left: '0.85rem',
                display: 'inline-flex',
                alignItems: 'center',
                color: isFocused ? 'var(--color-primary)' : 'var(--color-text-muted)',
                pointerEvents: 'none',
                transition: 'color var(--transition-fast)',
              }}
            >
              {leftIcon}
            </span>
          )}
          <input
            ref={ref}
            id={inputId}
            onFocus={handleFocus}
            onBlur={handleBlur}
            style={{
              width: '100%',
              minHeight: '44px',
              padding: leftIcon
                ? '0.65rem 0.85rem 0.65rem 2.65rem'
                : rightIcon
                ? '0.65rem 2.65rem 0.65rem 0.85rem'
                : '0.65rem 0.85rem',
              borderRadius: 'var(--radius-md)',
              border: `1.5px solid ${
                error
                  ? 'var(--color-error)'
                  : isFocused
                  ? 'var(--color-border-focus)'
                  : 'var(--color-border)'
              }`,
              boxShadow: isFocused
                ? error
                  ? '0 0 0 3px rgba(76, 61, 25, 0.18)'
                  : '0 0 0 3px rgba(136, 144, 99, 0.25)'
                : 'none',
              backgroundColor: 'var(--color-surface)',
              color: 'var(--color-text-primary)',
              fontSize: 'var(--font-size-base)',
              fontFamily: props.type === 'number' ? 'var(--font-tertiary)' : 'var(--font-primary)',
              outline: 'none',
              transition: 'border-color var(--transition-fast), box-shadow var(--transition-fast)',
              boxSizing: 'border-box',
              ...style,
            }}
            {...props}
          />
          {rightIcon && (
            <span
              style={{
                position: 'absolute',
                right: '0.85rem',
                display: 'inline-flex',
                alignItems: 'center',
                color: 'var(--color-text-muted)',
              }}
            >
              {rightIcon}
            </span>
          )}
        </div>
        {error && (
          <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-error)', fontWeight: 500 }}>
            {error}
          </span>
        )}
        {helperText && !error && (
          <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
            {helperText}
          </span>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

