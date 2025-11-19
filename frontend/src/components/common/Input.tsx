import { InputHTMLAttributes, TextareaHTMLAttributes, forwardRef } from 'react'
import clsx from 'clsx'

interface BaseInputProps {
  label?: string
  error?: string
  helperText?: string
}

type InputProps = BaseInputProps &
  (
    | (InputHTMLAttributes<HTMLInputElement> & { type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search' })
    | (TextareaHTMLAttributes<HTMLTextAreaElement> & { type: 'textarea' })
  )

export const Input = forwardRef<HTMLInputElement | HTMLTextAreaElement, InputProps>(
  ({ label, error, helperText, type = 'text', className, ...props }, ref) => {
    const isTextarea = type === 'textarea'

    const inputClasses = clsx(
      'w-full px-4 py-2 border rounded-md transition-colors',
      'focus:outline-none focus:ring-2 focus:ring-offset-1',
      {
        'border-red-300 focus:ring-red-500': error,
        'border-gray-300 focus:ring-primary-500': !error,
        'bg-gray-50 cursor-not-allowed': props.disabled,
        'resize-none': isTextarea,
      },
      className
    )

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}

        {isTextarea ? (
          <textarea
            ref={ref as React.Ref<HTMLTextAreaElement>}
            className={inputClasses}
            rows={4}
            {...(props as TextareaHTMLAttributes<HTMLTextAreaElement>)}
          />
        ) : (
          <input
            ref={ref as React.Ref<HTMLInputElement>}
            type={type}
            className={inputClasses}
            {...(props as InputHTMLAttributes<HTMLInputElement>)}
          />
        )}

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

Input.displayName = 'Input'
