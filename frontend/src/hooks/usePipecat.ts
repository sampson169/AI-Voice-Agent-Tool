import { useState, useEffect, useRef, useCallback } from 'react';
import { isDebugMode } from '../utils/config';

export const usePipecat = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [callDuration, setCallDuration] = useState(0);
  const [isListening, setIsListening] = useState(false);
  const webSocketRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const speechRecognitionRef = useRef<any>(null);
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

  const cleanupWebSocket = useCallback(() => {
    if (webSocketRef.current) {
      try {
        webSocketRef.current.close();
        webSocketRef.current = null;
      } catch (error) {
      }
    }
  }, []);

  const cleanupAudio = useCallback(() => {
    if (mediaRecorderRef.current) {
      try {
        mediaRecorderRef.current.stop();
        mediaRecorderRef.current = null;
      } catch (error) {
      }
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    if (speechRecognitionRef.current) {
      try {
        speechRecognitionRef.current.stop();
        speechRecognitionRef.current = null;
      } catch (error) {
      }
    }
    
    setIsListening(false);
  }, []);

  const setupSpeechRecognition = useCallback(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      if (isDebugMode()) {
        console.warn('Speech recognition not supported in this browser');
      }
      return null;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        }
      }

      if (finalTranscript.trim()) {
        setTranscript(prev => prev + `Driver: ${finalTranscript.trim()}\n\n`);
        
        setTimeout(() => {
          const responses = [
            "Got it, thank you for that update.",
            "I understand. What's your current location?",
            "Okay, and what's your estimated arrival time?",
            "Is everything secure with the load?",
            "Thanks for letting me know. Drive safely!",
            "I'll make note of that in the system."
          ];
          const randomResponse = responses[Math.floor(Math.random() * responses.length)];
          setTranscript(prev => prev + `AI Dispatcher: ${randomResponse}\n\n`);
        }, 1500 + Math.random() * 1000);
      }
    };

    recognition.onerror = (event: any) => {
      if (isDebugMode()) {
        console.error('Speech recognition error:', event.error);
      }
      if (event.error === 'not-allowed') {
        setError('Microphone access denied. Please allow microphone access and try again.');
      }
    };

    recognition.onend = () => {
      setIsListening(false);
      if (isConnected) {
        setTimeout(() => {
          try {
            recognition.start();
          } catch (error) {
          }
        }, 100);
      }
    };

    return recognition;
  }, [isConnected]);

  const startVoiceCapture = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const recognition = setupSpeechRecognition();
      if (recognition) {
        speechRecognitionRef.current = recognition;
        recognition.start();
      }

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

    } catch (error: any) {
      setError(`Voice capture failed: ${error.message}`);
      if (isDebugMode()) {
        console.error('Voice capture error:', error);
      }
    }
  }, [setupSpeechRecognition]);

  const startCall = useCallback(async (webCallLink: string) => {
    try {
      setError(null);
      setIsLoading(true);
      
      await startVoiceCapture();
      
      if (webCallLink.includes('your-pipecat-server.com')) {
        
        setTimeout(() => {
          setIsConnected(true);
          setIsLoading(false);
          setError(null);
          startTimer();
        }, 1500);
        
        return;
      }

      cleanupWebSocket();
      
      const ws = new WebSocket(webCallLink);
      
      ws.onopen = () => {
        handleConnected();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'transcript') {
            setTranscript(prev => prev + `${data.speaker}: ${data.text}\n\n`);
          } else if (data.type === 'error') {
            setError(data.message);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = () => {
        const errorMessage = 'PIPECAT connection error';
        setError(errorMessage);
        setIsConnected(false);
        setIsLoading(false);
        stopTimer();
      };

      ws.onclose = () => {
        setIsConnected(false);
        setIsLoading(false);
        stopTimer();
      };

      webSocketRef.current = ws;

      connectionTimeoutRef.current = window.setTimeout(() => {
        if (isLoading && !isConnected) {
          setError('Connection timeout - switching to demo mode');
          handleConnected();
        }
      }, 10000);

    } catch (error: any) {
      const errorMessage = `Failed to start PIPECAT call: ${error.message || 'Unknown error'}`;
      setError(errorMessage);
      setIsConnected(false);
      setIsLoading(false);
    }
  }, [cleanupWebSocket, isLoading, isConnected, handleConnected, startTimer, stopTimer]);

  const endCall = useCallback(() => {
    try {
      cleanupWebSocket();
      cleanupAudio();
      setIsConnected(false);
      setIsLoading(false);
      setError(null);
      stopTimer();
      clearConnectionTimeout();
    } catch (error: any) {
    }
  }, [cleanupWebSocket, cleanupAudio, stopTimer, clearConnectionTimeout]);

  useEffect(() => {
    return () => {
      cleanupWebSocket();
      cleanupAudio();
      stopTimer();
      clearConnectionTimeout();
    };
  }, [cleanupWebSocket, cleanupAudio, stopTimer, clearConnectionTimeout]);

  return {
    isConnected,
    isLoading,
    transcript,
    error,
    callDuration,
    isListening,
    startCall,
    endCall,
    resetCall,
    setTranscript
  };
};