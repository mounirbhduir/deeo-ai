import { SelectHTMLAttributes, forwardRef } from 'react'
import clsx from 'clsx'
import { ChevronDown } from 'lucide-react'

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  helperText?: string
  options: Array<{ value: string; label: string }>
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, helperText, options, className, ...props }, ref) => {
    // Ensure accessibility: if no label is visible, aria-label should be provided
    const selectProps = {
      ...props,
      // Add aria-label warning in console if neither label nor aria-label exists
      ...((!label && !props['aria-label']) && {
        'aria-label': 'Select option' // Default fallback
      })
    }

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}

        <div className="relative">
          <select
            ref={ref}
            className={clsx(
              'w-full px-4 py-2 pr-10 border rounded-md appearance-none transition-colors',
              'focus:outline-none focus:ring-2 focus:ring-offset-1',
              {
                'border-red-300 focus:ring-red-500': error,
                'border-gray-300 focus:ring-primary-500': !error,
                'bg-gray-50 cursor-not-allowed': props.disabled,
              },
              className
            )}
            {...selectProps}
          >
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
        </div>

        {error && (
          <p className="mt-1 text-sm text-red-600">{error}</p>
        )}

        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    )
  }
)

Select.displayName = 'Select'
