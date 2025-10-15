export const MESSAGES = {
    VALIDATION: {
        REQUIRED_DRIVER_LOAD: 'Please enter driver name and load number',
        MICROPHONE_ACCESS_DENIED: 'Microphone access denied',
        CALL_START_FAILED: 'Failed to start call',
        CHECK_CONFIGURATION: 'Please check your configuration and try again'
    },

    STATUS: {
        CALL_IN_PROGRESS: 'Call in progress...',
        CONNECTING: 'Connecting...',
        CONNECTED: 'Connected',
        DISCONNECTED: 'Disconnected',
        MUTED: 'Muted',
        UNMUTED: 'Unmuted'
    },

    ACTIONS: {
        SAVE_CONFIGURATION: 'Save Configuration',
        START_TEST_CALL: 'Start Test Call',
        END_CALL: 'End Call',
        NEW_CALL: 'New Call',
        EXPORT_RESULTS: 'Export',
        BACK_TO_CONFIG: 'Back to Configuration',
        TRY_AGAIN: 'Try Again',
        RETRY: 'Retry'
    },

    ERRORS: {
        SOMETHING_WENT_WRONG: 'Something went wrong',
        ERROR_OCCURRED: 'An error occurred while processing your request. Please refresh the page and try again.',
        SHOW_ERROR_DETAILS: 'Show error details',
        CALL_FAILED: 'Call failed to start',
        CONNECTION_LOST: 'Connection lost',
        AUDIO_ERROR: 'Audio error occurred',
        NETWORK_ERROR: 'Network error occurred',
        UNKNOWN_ERROR: 'Unknown error occurred'
    },

    SUCCESS: {
        CONFIG_SAVED: 'Configuration saved successfully',
        CALL_COMPLETED: 'Call completed successfully',
        EXPORT_COMPLETED: 'Results exported successfully'
    }
} as const;

export const LABELS = {
    AGENT_NAME: 'Agent Name',
    SCENARIO_TYPE: 'Scenario Type',
    AGENT_PROMPT: 'Agent Prompt',
    VOICE_SETTINGS: 'Voice Settings',
    EMERGENCY_PHRASES: 'Emergency Trigger Phrases',
    DRIVER_NAME: 'Driver Name',
    PHONE_NUMBER: 'Phone Number',
    LOAD_NUMBER: 'Load Number',
    CALL_TYPE: 'Call Type',
    DURATION: 'Duration',
    TIMESTAMP: 'Timestamp',
    CALL_OUTCOME: 'Call Outcome',
    STRUCTURED_SUMMARY: 'Structured Summary',
    EMERGENCY_DETAILS: 'Emergency Details',
    CALL_TRANSCRIPT: 'Call Transcript'
} as const;

export const PLACEHOLDERS = {
    AGENT_NAME: 'Enter agent name...',
    DRIVER_NAME: 'Enter driver name...',
    PHONE_NUMBER: 'Enter phone number...',
    LOAD_NUMBER: 'Enter load number...',
    EMERGENCY_PHRASES: 'emergency, accident, breakdown, medical...',
    SEPARATE_WITH_COMMAS: 'Separate phrases with commas'
} as const;