export interface AppError {
    code: string;
    message: string;
    userMessage: string;
    originalError?: Error;
    context?: Record<string, unknown>;
}

export type ErrorSeverity = 'low' | 'medium' | 'high' | 'critical';

export class ApplicationError extends Error {
    public readonly code: string;
    public readonly userMessage: string;
    public readonly severity: ErrorSeverity;
    public readonly context?: Record<string, unknown>;

    constructor(
        code: string,
        message: string,
        userMessage: string,
        severity: ErrorSeverity = 'medium',
        context?: Record<string, unknown>
    ) {
        super(message);
        this.name = 'ApplicationError';
        this.code = code;
        this.userMessage = userMessage;
        this.severity = severity;
        this.context = context;
    }
}

export const ERROR_CODES = {
    NETWORK_ERROR: 'NETWORK_ERROR',
    API_ERROR: 'API_ERROR',
    TIMEOUT_ERROR: 'TIMEOUT_ERROR',

    MICROPHONE_ACCESS_DENIED: 'MICROPHONE_ACCESS_DENIED',
    AUDIO_DEVICE_ERROR: 'AUDIO_DEVICE_ERROR',
    AUDIO_PROCESSING_ERROR: 'AUDIO_PROCESSING_ERROR',

    CALL_START_FAILED: 'CALL_START_FAILED',
    CALL_CONNECTION_LOST: 'CALL_CONNECTION_LOST',
    CALL_ENDED_UNEXPECTEDLY: 'CALL_ENDED_UNEXPECTEDLY',

    INVALID_INPUT: 'INVALID_INPUT',
    MISSING_REQUIRED_FIELD: 'MISSING_REQUIRED_FIELD',
    INVALID_CONFIGURATION: 'INVALID_CONFIGURATION',

    UNKNOWN_ERROR: 'UNKNOWN_ERROR',
    INITIALIZATION_ERROR: 'INITIALIZATION_ERROR'
} as const;

export function createError(
    code: keyof typeof ERROR_CODES,
    technicalMessage: string,
    userMessage: string,
    severity: ErrorSeverity = 'medium',
    context?: Record<string, unknown>
): ApplicationError {
    return new ApplicationError(code, technicalMessage, userMessage, severity, context);
}

export function handleApiError(error: unknown, context?: Record<string, unknown>): ApplicationError {
    if (error instanceof ApplicationError) {
        return error;
    }

    if (error instanceof Error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            return createError(
                'NETWORK_ERROR',
                `Network request failed: ${error.message}`,
                'Unable to connect to the server. Please check your internet connection and try again.',
                'high',
                { originalError: error.message, ...context }
            );
        }

        if (error.message.includes('timeout')) {
            return createError(
                'TIMEOUT_ERROR',
                `Request timeout: ${error.message}`,
                'The request took too long to complete. Please try again.',
                'medium',
                { originalError: error.message, ...context }
            );
        }

        return createError(
            'API_ERROR',
            error.message,
            'An error occurred while communicating with the server. Please try again.',
            'medium',
            { originalError: error.message, ...context }
        );
    }

    return createError(
        'UNKNOWN_ERROR',
        'Unknown error occurred',
        'An unexpected error occurred. Please try again.',
        'medium',
        { originalError: String(error), ...context }
    );
}

export function handleMediaError(error: unknown): ApplicationError {
    if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
            return createError(
                'MICROPHONE_ACCESS_DENIED',
                `Microphone access denied: ${error.message}`,
                'Microphone access is required for voice calls. Please allow microphone access in your browser settings.',
                'high',
                { originalError: error.message }
            );
        }

        if (error.name === 'NotFoundError') {
            return createError(
                'AUDIO_DEVICE_ERROR',
                `Audio device not found: ${error.message}`,
                'No microphone device found. Please check that your microphone is connected and try again.',
                'high',
                { originalError: error.message }
            );
        }

        return createError(
            'AUDIO_PROCESSING_ERROR',
            error.message,
            'An error occurred with audio processing. Please check your microphone and try again.',
            'medium',
            { originalError: error.message }
        );
    }

    return createError(
        'UNKNOWN_ERROR',
        'Unknown media error',
        'An unexpected audio error occurred. Please try again.',
        'medium',
        { originalError: String(error) }
    );
}

export function logError(error: ApplicationError): void {
    const logLevel = getLogLevel(error.severity);

    console[logLevel](`[${error.code}] ${error.message}`, {
        userMessage: error.userMessage,
        severity: error.severity,
        context: error.context,
        timestamp: new Date().toISOString()
    });
}

function getLogLevel(severity: ErrorSeverity): 'error' | 'warn' | 'info' {
    switch (severity) {
        case 'critical':
        case 'high':
            return 'error';
        case 'medium':
            return 'warn';
        case 'low':
            return 'info';
        default:
            return 'warn';
    }
}