import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 m-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Something went wrong</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>An error occurred while processing your request. Please refresh the page and try again.</p>
                {this.state.error && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-red-600 hover:text-red-800">
                      Show error details
                    </summary>
                    <pre className="mt-2 text-xs bg-red-100 p-2 rounded overflow-auto">
                      {this.state.error.message}
                    </pre>
                  </details>
                )}
              </div>
              <div className="mt-4">
                <button
                  onClick={() => this.setState({ hasError: false, error: undefined })}
                  className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;