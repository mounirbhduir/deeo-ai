import { ReactNode, useState, useRef, useEffect } from 'react'
import { createPortal } from 'react-dom'

interface TooltipProps {
  content: string
  children: ReactNode
  position?: 'top' | 'bottom' | 'left' | 'right'
}

export function Tooltip({
  content,
  children,
  position = 'top',
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [coords, setCoords] = useState({ x: 0, y: 0 })
  const triggerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isVisible && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect()
      const tooltipOffset = 8

      let x = 0
      let y = 0

      switch (position) {
        case 'top':
          x = rect.left + rect.width / 2
          y = rect.top - tooltipOffset
          break
        case 'bottom':
          x = rect.left + rect.width / 2
          y = rect.bottom + tooltipOffset
          break
        case 'left':
          x = rect.left - tooltipOffset
          y = rect.top + rect.height / 2
          break
        case 'right':
          x = rect.right + tooltipOffset
          y = rect.top + rect.height / 2
          break
      }

      setCoords({ x, y })
    }
  }, [isVisible, position])

  const tooltipElement = isVisible
    ? createPortal(
        <div
          className="fixed z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-md shadow-lg pointer-events-none whitespace-nowrap"
          style={{
            left: `${coords.x}px`,
            top: `${coords.y}px`,
            transform:
              position === 'top' || position === 'bottom'
                ? 'translateX(-50%)'
                : position === 'left'
                ? 'translate(-100%, -50%)'
                : 'translateY(-50%)',
          }}
        >
          {content}
        </div>,
        document.body
      )
    : null

  return (
    <>
      <div
        ref={triggerRef}
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        className="inline-block"
      >
        {children}
      </div>
      {tooltipElement}
    </>
  )
}
