import { useState, useCallback, useEffect } from 'react';
import { ApplicationError, logError } from '../utils/errorHandling';

export interface ErrorState {
    error: ApplicationError | null;
    isVisible: boolean;
}

export interface UseErrorReturn {
    errorState: ErrorState;
    showError: (error: ApplicationError) => void;
    clearError: () => void;
    retryAction?: () => void;
    setRetryAction: (action: (() => void) | undefined) => void;
}

export function useError(autoClearTimeout = 10000): UseErrorReturn {
    const [errorState, setErrorState] = useState<ErrorState>({
        error: null,
        isVisible: false
    });
    const [retryAction, setRetryAction] = useState<(() => void) | undefined>();

    const showError = useCallback((error: ApplicationError) => {
        logError(error);
        setErrorState({
            error,
            isVisible: true
        });
    }, []);

    const clearError = useCallback(() => {
        setErrorState({
            error: null,
            isVisible: false
        });
        setRetryAction(undefined);
    }, []);

    useEffect(() => {
        if (errorState.isVisible && errorState.error && errorState.error.severity !== 'critical') {
            const timer = setTimeout(clearError, autoClearTimeout);
            return () => clearTimeout(timer);
        }
    }, [errorState.isVisible, errorState.error, autoClearTimeout, clearError]);

    return {
        errorState,
        showError,
        clearError,
        retryAction,
        setRetryAction
    };
}