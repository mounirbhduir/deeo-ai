/**
 * ErrorBoundary Component - DEFENSIVE PROGRAMMING
 *
 * Prevents entire page crashes by catching JavaScript errors in child components.
 * Displays a user-friendly fallback UI instead of white screen.
 */

import { Component, ReactNode, ErrorInfo } from 'react'
import { Alert } from './Alert'
import { Button } from './Button'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // Update state so the next render shows the fallback UI
    return {
      hasError: true,
      error,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error details for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    this.setState({
      error,
      errorInfo,
    })
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback UI if provided
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default fallback UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-2xl w-full">
            <Alert variant="error" className="mb-4">
              <div className="space-y-4">
                <div>
                  <h2 className="text-lg font-semibold mb-2">
                    Une erreur est survenue
                  </h2>
                  <p className="text-sm">
                    Désolé, une erreur inattendue s'est produite lors du chargement de cette page.
                    Cela peut être dû à des données manquantes ou incompatibles.
                  </p>
                </div>

                {process.env.NODE_ENV === 'development' && this.state.error && (
                  <details className="text-sm">
                    <summary className="cursor-pointer font-medium mb-2">
                      Détails de l'erreur (développement uniquement)
                    </summary>
                    <pre className="bg-gray-100 p-3 rounded overflow-auto text-xs">
                      {this.state.error.toString()}
                      {this.state.errorInfo?.componentStack}
                    </pre>
                  </details>
                )}

                <div className="flex gap-3">
                  <Button
                    variant="primary"
                    onClick={this.handleReset}
                  >
                    Réessayer
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={() => window.location.href = '/'}
                  >
                    Retour à l'accueil
                  </Button>
                </div>
              </div>
            </Alert>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
