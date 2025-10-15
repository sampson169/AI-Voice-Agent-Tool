import React, { useState, useEffect } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import ErrorDisplay from './ui/ErrorDisplay';
import { createError } from '../utils/errorHandling';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorState {
  hasError: boolean;
  error?: Error;
}

const ErrorBoundary: React.FC<Props> = ({ children, fallback, onError }) => {
  const [errorState, setErrorState] = useState<ErrorState>({ hasError: false });

  useEffect(() => {
    if (errorState.hasError) {
      setErrorState({ hasError: false });
    }
  }, [children]);

  const handleRetry = () => {
    setErrorState({ hasError: false, error: undefined });
  };

  const handleErrorClose = () => {
    if (errorState.error?.name === 'ChunkLoadError') {
      window.location.reload();
    } else {
      setErrorState({ hasError: false, error: undefined });
    }
  };

  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      const error = new Error(event.message);
      error.stack = event.error?.stack;
      setErrorState({ hasError: true, error });
      onError?.(error, { componentStack: '' });
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      const error = new Error(event.reason?.message || 'Unhandled Promise Rejection');
      setErrorState({ hasError: true, error });
      onError?.(error, { componentStack: '' });
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, [onError]);

  if (errorState.hasError && errorState.error) {
    if (fallback) {
      return <>{fallback}</>;
    }

    const appError = createError(
      'UNKNOWN_ERROR',
      errorState.error.message,
      'An unexpected error occurred. The application may need to be refreshed.',
      'high',
      {
        stack: errorState.error.stack,
        name: errorState.error.name
      }
    );

    return (
      <div className="p-4 m-4">
        <ErrorDisplay
          error={appError}
          isVisible={true}
          onClose={handleErrorClose}
          onRetry={handleRetry}
        />
      </div>
    );
  }

  return <>{children}</>;
};

export default ErrorBoundary;