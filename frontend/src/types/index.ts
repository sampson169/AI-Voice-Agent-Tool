export interface AgentConfig {
  id?: string;
  name: string;
  prompt: string;
  scenarioType?: string;
  voiceSettings: {
    voiceId: string;
    speed: number;
    temperature: number;
    backchanneling: boolean;
    fillerWords: boolean;
    interruptionSensitivity: 'low' | 'medium' | 'high';
  };
  emergencyPhrases: string[];
  structuredFields: StructuredField[];
}

export interface CallRequest {
  driverName: string;
  phoneNumber?: string;
  loadNumber: string;
  agentId: string;
  callType: 'phone' | 'web';
}

export interface CallResult {
  id: string;
  callRequest: CallRequest;
  transcript: string;
  summary: CallSummary;
  timestamp: string;
  duration: number;
}

export interface CallSummary {
  call_outcome: string;
  driver_status: string;
  current_location: string;
  eta: string;
  delay_reason: string;
  unloading_status: string;
  pod_reminder_acknowledged: boolean;
  emergency_type?: string;
  safety_status?: string;
  injury_status?: string;
  emergency_location?: string;
  load_secure?: boolean;
  escalation_status?: string;
}

export interface StructuredField {
  key: keyof CallSummary;
  label: string;
  type: 'text' | 'select' | 'boolean';
  options?: string[];
}

export type AppView = 'config' | 'call' | 'results' | 'analytics';