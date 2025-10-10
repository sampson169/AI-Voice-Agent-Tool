import { useState, useEffect, useRef } from 'react';
import { RetellWebClient } from 'retell-client-js-sdk';

export const useRetell = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const clientRef = useRef<RetellWebClient | null>(null);

  const initializeClient = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const client = new RetellWebClient();
      
      client.on('conversationStarted', () => {
        console.log('Conversation started');
        setIsConnected(true);
        setIsLoading(false);
      });

      client.on('conversationEnded', ({ code, reason }) => {
        console.log('Conversation ended:', code, reason);
        setIsConnected(false);
      });

      client.on('error', (error) => {
        console.error('Retell client error:', error);
        setError(`Connection error: ${error.message || 'Unknown error'}`);
        setIsConnected(false);
        setIsLoading(false);
      });

      client.on('update', (update) => {
        if (update.transcript && update.transcript.length > 0) {
          const latestTranscript = update.transcript
            .map((t: any) => `${t.role === 'agent' ? 'AI' : 'You'}: ${t.content}`)
            .join('\n\n');
          setTranscript(latestTranscript + '\n\n');
        }
      });

      client.on('metadata', (metadata) => {
        console.log('Call metadata:', metadata);
      });
      
      clientRef.current = client;
      setIsLoading(false);
      
    } catch (error: any) {
      console.error('Failed to initialize Retell client:', error);
      setError(`Initialization failed: ${error.message || 'Unknown error'}`);
      setIsLoading(false);
    }
  };

  const startCall = async (accessToken: string, callId?: string) => {
    try {
      setError(null);
      
      if (!clientRef.current) {
        await initializeClient();
      }

      if (!clientRef.current) {
        throw new Error('Failed to initialize Retell client');
      }

      setIsLoading(true);
      
      await clientRef.current.startCall({
        accessToken,
        sampleRate: 24000
      });

    } catch (error: any) {
      console.error('Failed to start call:', error);
      setError(`Failed to start call: ${error.message || 'Unknown error'}`);
      setIsConnected(false);
      setIsLoading(false);
    }
  };

  const endCall = () => {
    try {
      clientRef.current?.stopCall();
      setIsConnected(false);
      setError(null);
    } catch (error: any) {
      console.error('Error ending call:', error);
    }
  };

  useEffect(() => {
    return () => {
      if (clientRef.current) {
        try {
          clientRef.current.stopCall();
        } catch (error) {
          console.error('Error cleaning up Retell client:', error);
        }
      }
    };
  }, []);

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