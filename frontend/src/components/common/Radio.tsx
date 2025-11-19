import { InputHTMLAttributes, forwardRef } from 'react'
import clsx from 'clsx'

interface RadioProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string
}

export const Radio = forwardRef<HTMLInputElement, RadioProps>(
  ({ label, className, ...props }, ref) => {
    return (
      <label className="flex items-center space-x-2 cursor-pointer">
        <div className="relative">
          <input
            ref={ref}
            type="radio"
            className="sr-only peer"
            {...props}
          />
          <div
            className={clsx(
              'h-5 w-5 border-2 rounded-full transition-all',
              'peer-checked:border-primary-600',
              'peer-focus:ring-2 peer-focus:ring-primary-500 peer-focus:ring-offset-1',
              'peer-disabled:bg-gray-100 peer-disabled:cursor-not-allowed',
              'border-gray-300',
              className
            )}
          >
            <div className="absolute inset-0 m-1 rounded-full bg-primary-600 opacity-0 peer-checked:opacity-100 transition-opacity" />
          </div>
        </div>
        {label && (
          <span className="text-sm text-gray-700 select-none">
            {label}
          </span>
        )}
      </label>
    )
  }
)

Radio.displayName = 'Radio'
