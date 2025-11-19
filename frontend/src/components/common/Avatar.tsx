import { ImgHTMLAttributes } from 'react'
import clsx from 'clsx'
import { User } from 'lucide-react'

interface AvatarProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'src'> {
  src?: string
  alt: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  fallback?: string
}

export function Avatar({
  src,
  alt,
  size = 'md',
  fallback,
  className,
  ...props
}: AvatarProps) {
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-10 w-10',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16',
  }

  if (!src) {
    return (
      <div
        className={clsx(
          'flex items-center justify-center rounded-full bg-gray-200 text-gray-600',
          sizeClasses[size],
          className
        )}
      >
        {fallback ? (
          <span className="font-medium text-sm">
            {fallback.substring(0, 2).toUpperCase()}
          </span>
        ) : (
          <User className="h-1/2 w-1/2" />
        )}
      </div>
    )
  }

  return (
    <img
      src={src}
      alt={alt}
      className={clsx(
        'rounded-full object-cover',
        sizeClasses[size],
        className
      )}
      {...props}
    />
  )
}
