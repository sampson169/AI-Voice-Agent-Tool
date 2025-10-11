import { useState, useEffect, useRef, useCallback } from 'react';
import { RetellWebClient } from 'retell-client-js-sdk';
import config, { isDebugMode } from '../utils/config';

export const useRetell = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const clientRef = useRef<RetellWebClient | null>(null);
  const isInitializedRef = useRef(false);

  const cleanupClient = useCallback(() => {
    if (clientRef.current) {
      try {
        clientRef.current.stopCall();
        clientRef.current = null;
        isInitializedRef.current = false;
      } catch (error) {
        if (isDebugMode()) {
          console.warn('Error during client cleanup:', error);
        }
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
        setIsConnected(true);
        setIsLoading(false);
        setError(null);
      });

      client.on('conversationEnded', () => {
        setIsConnected(false);
        setIsLoading(false);
      });

      client.on('error', (error) => {
        const errorMessage = `Connection error: ${error.message || 'Unknown error'}`;
        if (isDebugMode()) {
          console.error('Retell error:', error);
        }
        setError(errorMessage);
        setIsConnected(false);
        setIsLoading(false);
      });

      client.on('update', (update) => {
        if (update.transcript && update.transcript.length > 0) {
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

    } catch (error: any) {
      const errorMessage = `Failed to start call: ${error.message || 'Unknown error'}`;
      setError(errorMessage);
      setIsConnected(false);
      setIsLoading(false);
      if (isDebugMode()) {
        console.error('Start call error:', error);
      }
    }
  }, [initializeClient]);

  const endCall = useCallback(() => {
    try {
      if (clientRef.current) {
        clientRef.current.stopCall();
      }
      setIsConnected(false);
      setIsLoading(false);
      setError(null);
    } catch (error: any) {
      if (isDebugMode()) {
        console.warn('Error ending call:', error);
      }
    }
  }, []);

  useEffect(() => {
    return () => {
      cleanupClient();
    };
  }, [cleanupClient]);

  return {
    isConnected,
    isLoading,
    transcript,
    error,
    startCall,
    endCall,
    setTranscript
  };
};