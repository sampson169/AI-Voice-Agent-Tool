import { useState, useEffect, useRef, useCallback } from 'react';
import { RetellWebClient } from 'retell-client-js-sdk';
import config, { isDebugMode } from '../utils/config';

export const useRetell = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [callDuration, setCallDuration] = useState(0);
  const clientRef = useRef<RetellWebClient | null>(null);
  const isInitializedRef = useRef(false);
  const timerRef = useRef<number | null>(null);
  const callStartTimeRef = useRef<number | null>(null);
  const connectionTimeoutRef = useRef<number | null>(null);

  const startTimer = useCallback(() => {
    if (timerRef.current) {
      return;
    }
    
    callStartTimeRef.current = Date.now();
    setCallDuration(0);
    
    timerRef.current = window.setInterval(() => {
      if (callStartTimeRef.current) {
        const elapsed = Math.floor((Date.now() - callStartTimeRef.current) / 1000);
        setCallDuration(elapsed);
      }
    }, 1000);
  }, []);

  const stopTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    callStartTimeRef.current = null;
  }, []);

  const clearConnectionTimeout = useCallback(() => {
    if (connectionTimeoutRef.current) {
      clearTimeout(connectionTimeoutRef.current);
      connectionTimeoutRef.current = null;
    }
  }, []);

  const handleConnected = useCallback(() => {
    if (!isConnected) {
      setIsConnected(true);
      setIsLoading(false);
      setError(null);
      startTimer();
      clearConnectionTimeout();
    }
  }, [isConnected, isLoading, startTimer, clearConnectionTimeout]);

  const resetCall = useCallback(() => {
    setTranscript('');
    setCallDuration(0);
    setError(null);
    setIsConnected(false);
    setIsLoading(false);
    stopTimer();
    clearConnectionTimeout();
  }, [stopTimer, clearConnectionTimeout]);

  const cleanupClient = useCallback(() => {
    if (clientRef.current) {
      try {
        clientRef.current.stopCall();
        clientRef.current = null;
        isInitializedRef.current = false;
      } catch (error) {
        
      }
    }
  }, []);

  const initializeClient = useCallback(async () => {
    if (isInitializedRef.current && clientRef.current) {
      return clientRef.current;
    }

    try {
      cleanupClient();
      
      const client = new RetellWebClient();
      
      client.on('conversationStarted', () => {
        handleConnected();
      });

      client.on('conversationEnded', () => {
        setIsConnected(false);
        setIsLoading(false);
        stopTimer();
        clearConnectionTimeout();
      });

      client.on('call_started', () => {
        handleConnected();
      });

      client.on('agent_start_talking', () => {
        handleConnected();
      });

      client.on('call_connected', () => {
        handleConnected();
      });

      client.on('room_connected', () => {
        handleConnected();
      });

      client.on('error', (error) => {
        const errorMessage = `Connection error: ${error.message || 'Unknown error'}`;
        if (isDebugMode()) {
          console.error('Retell error:', error);
        }
        
        if (error.message && error.message.includes('state mismatch')) {
          setTimeout(() => {
            if (isLoading) {
              handleConnected();
            }
          }, 1000);
        } else {
          setError(errorMessage);
          setIsConnected(false);
          setIsLoading(false);
          stopTimer();
          clearConnectionTimeout();
        }
      });

      client.on('update', (update) => {
        if (update.transcript && update.transcript.length > 0) {
          if (!isConnected && isLoading) {
            handleConnected();
          }
          
          const latestTranscript = update.transcript
            .map((t: any) => `${t.role === 'agent' ? 'AI' : 'You'}: ${t.content}`)
            .join('\n\n');
          
          let finalTranscript = latestTranscript + '\n\n';
          
          if (finalTranscript.length > config.maxTranscriptLength) {
            finalTranscript = '...' + finalTranscript.slice(-(config.maxTranscriptLength - 3));
          }
          
          setTranscript(finalTranscript);
        }
      });

      client.on('metadata', () => {
        
      });
      
      clientRef.current = client;
      isInitializedRef.current = true;
      
      return client;
      
    } catch (error: any) {
      const errorMessage = `Initialization failed: ${error.message || 'Unknown error'}`;
      setError(errorMessage);
      setIsLoading(false);
      throw new Error(errorMessage);
    }
  }, [cleanupClient]);

  const startCall = useCallback(async (accessToken: string) => {
    try {
      setError(null);
      setIsLoading(true);
      
      const client = await initializeClient();

      if (!client) {
        throw new Error('Failed to initialize Retell client');
      }

      await client.startCall({
        accessToken,
        sampleRate: config.retellSampleRate
      });

      connectionTimeoutRef.current = window.setTimeout(() => {
        if (isLoading && !isConnected) {
          handleConnected();
        }
      }, 5000);

      setTimeout(() => {
        if (isLoading && !isConnected) {
          handleConnected();
        }
      }, 1000);

    } catch (error: any) {
      const errorMessage = `Failed to start call: ${error.message || 'Unknown error'}`;
      setError(errorMessage);
      setIsConnected(false);
      setIsLoading(false);
    }
  }, [initializeClient, isLoading, isConnected, handleConnected]);

  const endCall = useCallback(() => {
    try {
      if (clientRef.current) {
        clientRef.current.stopCall();
      }
      setIsConnected(false);
      setIsLoading(false);
      setError(null);
      stopTimer();
      clearConnectionTimeout();
    } catch (error: any) {
      
    }
  }, [stopTimer, clearConnectionTimeout]);

  useEffect(() => {
    return () => {
      cleanupClient();
      stopTimer();
      clearConnectionTimeout();
    };
  }, [cleanupClient, stopTimer, clearConnectionTimeout]);

  return {
    isConnected,
    isLoading,
    transcript,
    error,
    callDuration,
    startCall,
    endCall,
    resetCall,
    setTranscript
  };
};