/**
 * SearchBar Component (Phase 4 - Step 5)
 *
 * Search bar for publications with real-time input and submit on enter.
 */

import { useState, useCallback, FormEvent, ChangeEvent } from 'react'
import { Input } from '../common/Input'
import { Button } from '../common/Button'

interface SearchBarProps {
  initialValue?: string
  onSearch: (query: string) => void
  placeholder?: string
}

export const SearchBar = ({
  initialValue = '',
  onSearch,
  placeholder = 'Rechercher des publications...',
}: SearchBarProps) => {
  const [value, setValue] = useState(initialValue)

  const handleSubmit = useCallback(
    (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault()
      onSearch(value)
    },
    [value, onSearch]
  )

  const handleChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setValue(e.target.value)
  }, [])

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <div className="flex-1">
        <Input
          type="search"
          value={value}
          onChange={handleChange}
          placeholder={placeholder}
          className="w-full"
        />
      </div>
      <Button type="submit" variant="primary">
        Rechercher
      </Button>
    </form>
  )
}
