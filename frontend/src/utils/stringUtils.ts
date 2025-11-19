/**
 * String utility functions
 */

/**
 * Get initials from a full name
 * @param name Full name (e.g., "John Doe")
 * @returns Initials (e.g., "JD")
 */
export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((part) => part.charAt(0))
    .join('')
    .substring(0, 2)
    .toUpperCase()
}
