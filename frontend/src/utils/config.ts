interface AppConfig {
  apiBaseUrl: string;
  apiTimeout: number;
  defaultAgentId: string;
  backupAgentId: string;
  retellSampleRate: number;
  retellTimeout: number;
  appName: string;
  appVersion: string;
  appDescription: string;
  devPort: number;
  nodeEnv: string;
  debugMode: boolean;
  callTimeout: number;
  maxTranscriptLength: number;
  autoScrollTranscript: boolean;
}

const config: AppConfig = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  apiTimeout: Math.max(parseInt(import.meta.env.VITE_API_TIMEOUT) || 10000, 5000),
  defaultAgentId: import.meta.env.VITE_DEFAULT_AGENT_ID || 'agent_b4902d2c6973a595dc4cf5ad55',
  backupAgentId: import.meta.env.VITE_BACKUP_AGENT_ID || '',
  retellSampleRate: Math.min(Math.max(parseInt(import.meta.env.VITE_RETELL_SAMPLE_RATE) || 24000, 8000), 48000),
  retellTimeout: Math.max(parseInt(import.meta.env.VITE_RETELL_TIMEOUT) || 30000, 10000),
  appName: import.meta.env.VITE_APP_NAME || 'Voice Agent Tool',
  appVersion: import.meta.env.VITE_APP_VERSION || '1.0.0',
  appDescription: import.meta.env.VITE_APP_DESCRIPTION || 'AI-powered voice agent',
  devPort: Math.max(parseInt(import.meta.env.VITE_DEV_PORT) || 5173, 3000),
  nodeEnv: import.meta.env.VITE_NODE_ENV || 'development',
  debugMode: import.meta.env.VITE_DEBUG_MODE === 'true',
  callTimeout: Math.max(parseInt(import.meta.env.VITE_CALL_TIMEOUT) || 60000, 30000),
  maxTranscriptLength: Math.max(parseInt(import.meta.env.VITE_MAX_TRANSCRIPT_LENGTH) || 10000, 1000),
  autoScrollTranscript: import.meta.env.VITE_AUTO_SCROLL_TRANSCRIPT !== 'false',
};

export const validateConfig = (): string[] => {
  const errors: string[] = [];
  
  if (!config.apiBaseUrl) {
    errors.push('VITE_API_BASE_URL is required');
  }
  
  if (!config.defaultAgentId) {
    errors.push('VITE_DEFAULT_AGENT_ID is required');
  }
  
  return errors;
};

export const isDevelopment = () => config.nodeEnv === 'development';
export const isProduction = () => config.nodeEnv === 'production';
export const isDebugMode = () => config.debugMode;

export default config;