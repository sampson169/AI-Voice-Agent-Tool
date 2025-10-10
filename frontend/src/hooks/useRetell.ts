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
        setIsConnected(true);
        setIsLoading(false);
      });

      client.on('conversationEnded', () => {
        setIsConnected(false);
      });

      client.on('error', (error) => {
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

      client.on('metadata', () => {
        // Handle metadata if needed
      });
      
      clientRef.current = client;
      setIsLoading(false);
      
    } catch (error: any) {
      setError(`Initialization failed: ${error.message || 'Unknown error'}`);
      setIsLoading(false);
    }
  };

  const startCall = async (accessToken: string) => {
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
      // Error ending call
    }
  };

  useEffect(() => {
    return () => {
      if (clientRef.current) {
        try {
          clientRef.current.stopCall();
        } catch (error) {
          // Error cleaning up client
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