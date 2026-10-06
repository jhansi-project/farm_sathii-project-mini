import React from 'react';

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  width?: string | number;
  height?: string | number;
  borderRadius?: string;
  circle?: boolean;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = '20px',
  borderRadius = 'var(--radius-md)',
  circle = false,
  style,
  className,
  ...props
}) => {
  return (
    <div
      className={`skeleton-shimmer ${className || ''}`}
      style={{
        width: circle ? height : width,
        height,
        borderRadius: circle ? 'var(--radius-full)' : borderRadius,
        display: 'inline-block',
        ...style,
      }}
      {...props}
    />
  );
};
