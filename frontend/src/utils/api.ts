import axios from 'axios';
import config from './config';
import type { AgentConfig, CallRequest, CallResult } from '../types';

const apiClient = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: config.apiTimeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  async createAgentConfig(config: Omit<AgentConfig, 'id'>): Promise<AgentConfig> {
    const response = await apiClient.post('/api/agents/', config);
    return response.data;
  },

  async getAgentConfigs(): Promise<AgentConfig[]> {
    const response = await apiClient.get('/api/agents/');
    return response.data;
  },

  async startCall(callRequest: CallRequest): Promise<{
    call_id: string;
    retell_call_id: string;
    status: string;
    web_call_link?: string;
    access_token?: string;
  }> {
    const backendRequest = {
      driver_name: callRequest.driverName,
      phone_number: callRequest.phoneNumber || null,
      load_number: callRequest.loadNumber,
      agent_id: callRequest.agentId || config.defaultAgentId,
      call_type: callRequest.callType
    };
    
    const response = await apiClient.post('/api/calls/start', backendRequest);
    return response.data;
  },

  async getCallResult(callId: string): Promise<CallResult> {
    const response = await apiClient.get(`/api/calls/${callId}/result`);
    return response.data;
  },

  async getAllCallResults(): Promise<CallResult[]> {
    const response = await apiClient.get('/api/calls/');
    return response.data;
  }
};