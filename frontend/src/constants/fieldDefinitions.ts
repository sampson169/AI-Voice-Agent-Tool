export interface StructuredField {
    key: string;
    label: string;
    type: 'text' | 'select' | 'boolean';
    options?: string[];
}

export const FIELD_DEFINITIONS = {
    CALL_OUTCOME: {
        key: 'call_outcome',
        label: 'Call Outcome',
        type: 'select' as const,
        options: ['In-Transit Update', 'Arrival Confirmation', 'Emergency Escalation']
    },

    DRIVER_STATUS: {
        key: 'driver_status',
        label: 'Driver Status',
        type: 'select' as const,
        options: ['Driving', 'Delayed', 'Arrived', 'Unloading']
    },

    CURRENT_LOCATION: {
        key: 'current_location',
        label: 'Current Location',
        type: 'text' as const
    },

    ETA: {
        key: 'eta',
        label: 'ETA',
        type: 'text' as const
    },

    DELAY_REASON: {
        key: 'delay_reason',
        label: 'Delay Reason',
        type: 'select' as const,
        options: ['Heavy Traffic', 'Weather', 'Mechanical', 'Loading/Unloading', 'None']
    },

    UNLOADING_STATUS: {
        key: 'unloading_status',
        label: 'Unloading Status',
        type: 'select' as const,
        options: ['In Door', 'Waiting for Lumper', 'Detention', 'N/A']
    },

    POD_REMINDER: {
        key: 'pod_reminder_acknowledged',
        label: 'POD Reminder',
        type: 'boolean' as const
    },

    EMERGENCY_TYPE: {
        key: 'emergency_type',
        label: 'Emergency Type',
        type: 'select' as const,
        options: ['Accident', 'Breakdown', 'Medical', 'Other']
    },

    SAFETY_STATUS: {
        key: 'safety_status',
        label: 'Safety Status',
        type: 'text' as const
    },

    INJURY_STATUS: {
        key: 'injury_status',
        label: 'Injury Status',
        type: 'text' as const
    },

    EMERGENCY_LOCATION: {
        key: 'emergency_location',
        label: 'Emergency Location',
        type: 'text' as const
    },

    LOAD_SECURE: {
        key: 'load_secure',
        label: 'Load Secure',
        type: 'boolean' as const
    },

    ESCALATION_STATUS: {
        key: 'escalation_status',
        label: 'Escalation Status',
        type: 'text' as const
    }
} as const;

export const SCENARIO_FIELDS = {
    GENERAL: [
        FIELD_DEFINITIONS.CALL_OUTCOME,
        FIELD_DEFINITIONS.DRIVER_STATUS,
        FIELD_DEFINITIONS.CURRENT_LOCATION,
        FIELD_DEFINITIONS.ETA,
        FIELD_DEFINITIONS.DELAY_REASON,
        FIELD_DEFINITIONS.UNLOADING_STATUS,
        FIELD_DEFINITIONS.POD_REMINDER,
        FIELD_DEFINITIONS.EMERGENCY_TYPE,
        FIELD_DEFINITIONS.SAFETY_STATUS,
        FIELD_DEFINITIONS.INJURY_STATUS,
        FIELD_DEFINITIONS.EMERGENCY_LOCATION,
        FIELD_DEFINITIONS.LOAD_SECURE,
        FIELD_DEFINITIONS.ESCALATION_STATUS
    ],

    DRIVER_CHECKIN: [
        { ...FIELD_DEFINITIONS.CALL_OUTCOME, options: ['In-Transit Update', 'Arrival Confirmation'] },
        FIELD_DEFINITIONS.DRIVER_STATUS,
        FIELD_DEFINITIONS.CURRENT_LOCATION,
        FIELD_DEFINITIONS.ETA,
        FIELD_DEFINITIONS.DELAY_REASON,
        FIELD_DEFINITIONS.UNLOADING_STATUS,
        FIELD_DEFINITIONS.POD_REMINDER
    ],

    EMERGENCY_PROTOCOL: [
        { ...FIELD_DEFINITIONS.CALL_OUTCOME, options: ['Emergency Escalation'] },
        FIELD_DEFINITIONS.EMERGENCY_TYPE,
        FIELD_DEFINITIONS.SAFETY_STATUS,
        FIELD_DEFINITIONS.INJURY_STATUS,
        FIELD_DEFINITIONS.EMERGENCY_LOCATION,
        FIELD_DEFINITIONS.LOAD_SECURE,
        FIELD_DEFINITIONS.ESCALATION_STATUS
    ]
} as const;