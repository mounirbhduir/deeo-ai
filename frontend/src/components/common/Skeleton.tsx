import { HTMLAttributes } from 'react'
import clsx from 'clsx'

interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  width?: string
  height?: string
  variant?: 'text' | 'circular' | 'rectangular'
}

export function Skeleton({
  width,
  height,
  variant = 'rectangular',
  className,
  ...props
}: SkeletonProps) {
  return (
    <div
      className={clsx(
        'animate-pulse bg-gray-200',
        {
          'rounded': variant === 'rectangular',
          'rounded-full': variant === 'circular',
          'rounded-md': variant === 'text',
        },
        className
      )}
      style={{ width, height }}
      {...props}
    />
  )
}
