import React from 'react';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({ size = 'md', color = 'currentColor' }) => {
  const sizeMap = {
    sm: 16,
    md: 24,
    lg: 36,
  };
  const dim = sizeMap[size];

  return (
    <svg
      style={{
        animation: 'farmsathi-spin 0.8s linear infinite',
        width: dim,
        height: dim,
        display: 'inline-block',
      }}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <style>{`
        @keyframes farmsathi-spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
      <circle cx="12" cy="12" r="10" strokeOpacity="0.25" />
      <path d="M12 2a10 10 0 0 1 10 10" />
    </svg>
  );
};
