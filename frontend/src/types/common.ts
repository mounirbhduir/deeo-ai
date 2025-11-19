export type Size = 'sm' | 'md' | 'lg'
export type Variant = 'default' | 'primary' | 'secondary' | 'ghost'
export type Status = 'success' | 'warning' | 'error' | 'info'

export interface BaseComponentProps {
  className?: string
  id?: string
}
