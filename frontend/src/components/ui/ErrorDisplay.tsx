import React from 'react';
import { AlertTriangle, X, RefreshCw } from 'lucide-react';
import { ApplicationError } from '../../utils/errorHandling';
import { MESSAGES } from '../../constants/messages';

interface ErrorDisplayProps {
  error: ApplicationError;
  isVisible: boolean;
  onClose: () => void;
  onRetry?: () => void;
  className?: string;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  isVisible,
  onClose,
  onRetry,
  className = ''
}) => {
  if (!isVisible || !error) {
    return null;
  }

  const getSeverityStyles = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 border-red-300 text-red-900';
      case 'high':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'medium':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'low':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getIconColor = (severity: string) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return 'text-red-500';
      case 'medium':
        return 'text-yellow-500';
      case 'low':
        return 'text-blue-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <div
      className={`rounded-lg border p-4 shadow-sm ${getSeverityStyles(error.severity)} ${className}`}
      role="alert"
      aria-live="polite"
    >
      <div className="flex items-start">
        <AlertTriangle 
          className={`h-5 w-5 mt-0.5 mr-3 flex-shrink-0 ${getIconColor(error.severity)}`}
          aria-hidden="true"
        />
        
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium mb-1">
            {error.severity === 'critical' ? 'Critical Error' : 'Error Occurred'}
          </h3>
          
          <p className="text-sm mb-2">
            {error.userMessage}
          </p>
          
          {import.meta.env?.DEV && error.context && (
            <details className="text-xs mt-2">
              <summary className="cursor-pointer hover:underline">
                Technical Details
              </summary>
              <pre className="mt-1 p-2 bg-black bg-opacity-10 rounded text-xs overflow-auto">
                {JSON.stringify({
                  code: error.code,
                  message: error.message,
                  context: error.context
                }, null, 2)}
              </pre>
            </details>
          )}
        </div>
        
        <div className="flex items-center space-x-2 ml-4">
          {onRetry && (
            <button
              onClick={onRetry}
              className="inline-flex items-center px-2 py-1 text-xs font-medium rounded hover:bg-black hover:bg-opacity-10 transition-colors"
              aria-label={MESSAGES.ACTIONS.RETRY}
            >
              <RefreshCw className="h-3 w-3 mr-1" />
              {MESSAGES.ACTIONS.RETRY}
            </button>
          )}
          
          <button
            onClick={onClose}
            className="inline-flex items-center justify-center w-6 h-6 rounded hover:bg-black hover:bg-opacity-10 transition-colors"
            aria-label="Close error message"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ErrorDisplay;