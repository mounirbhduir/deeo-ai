import { InputHTMLAttributes, forwardRef } from 'react'
import clsx from 'clsx'
import { Check } from 'lucide-react'

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, className, ...props }, ref) => {
    return (
      <label className="flex items-center space-x-2 cursor-pointer">
        <div className="relative">
          <input
            ref={ref}
            type="checkbox"
            className="sr-only peer"
            {...props}
          />
          <div
            className={clsx(
              'h-5 w-5 border-2 rounded transition-all flex items-center justify-center',
              'peer-checked:bg-primary-600 peer-checked:border-primary-600',
              'peer-focus:ring-2 peer-focus:ring-primary-500 peer-focus:ring-offset-1',
              'peer-disabled:bg-gray-100 peer-disabled:cursor-not-allowed',
              'border-gray-300',
              className
            )}
          >
            <Check className="h-4 w-4 text-white opacity-0 peer-checked:opacity-100 transition-opacity" />
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

Checkbox.displayName = 'Checkbox'
