import axios from 'axios';
import config from './config';
import type { AgentConfig, CallRequest, CallResult } from '../types';
import { handleApiError } from './errorHandling';

const apiClient = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: config.apiTimeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    throw handleApiError(error, { 
      url: error.config?.url, 
      method: error.config?.method 
    });
  }
);

export const api = {
  async createAgentConfig(config: Omit<AgentConfig, 'id'>): Promise<AgentConfig> {
    try {
      const response = await apiClient.post('/api/agents/', config);
      return response.data;
    } catch (error) {
      throw handleApiError(error, { operation: 'createAgentConfig' });
    }
  },

  async getAgentConfigs(): Promise<AgentConfig[]> {
    try {
      const response = await apiClient.get('/api/agents/');
      return response.data;
    } catch (error) {
      throw handleApiError(error, { operation: 'getAgentConfigs' });
    }
  },

  async startCall(callRequest: CallRequest): Promise<{
    call_id: string;
    retell_call_id: string;
    status: string;
    web_call_link?: string;
    access_token?: string;
  }> {
    try {
      const backendRequest = {
        driver_name: callRequest.driverName,
        phone_number: callRequest.phoneNumber || null,
        load_number: callRequest.loadNumber,
        agent_id: callRequest.agentId || config.defaultAgentId,
        call_type: callRequest.callType
      };
      
      const response = await apiClient.post('/api/calls/start', backendRequest);
      return response.data;
    } catch (error) {
      throw handleApiError(error, { 
        operation: 'startCall',
        callRequest: {
          driverName: callRequest.driverName,
          loadNumber: callRequest.loadNumber,
          callType: callRequest.callType
        }
      });
    }
  },

  async getCallResult(callId: string): Promise<CallResult> {
    try {
      const response = await apiClient.get(`/api/calls/${callId}/result`);
      return response.data;
    } catch (error) {
      throw handleApiError(error, { operation: 'getCallResult', callId });
    }
  },

  async getAllCallResults(): Promise<CallResult[]> {
    try {
      const response = await apiClient.get('/api/calls/');
      return response.data;
    } catch (error) {
      throw handleApiError(error, { operation: 'getAllCallResults' });
    }
  },

  async endCall(callId: string): Promise<void> {
    try {
      await apiClient.post(`/api/calls/${callId}/end`);
    } catch (error) {
      throw handleApiError(error, { operation: 'endCall', callId });
    }
  }
};