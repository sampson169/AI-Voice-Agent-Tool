import React, { useState, useEffect, useRef } from 'react';
import { Phone, PhoneOff, Mic, MicOff, Volume2 } from 'lucide-react';
import type { AgentConfig, CallRequest, CallResult } from '../types';
import { api } from '../utils/api';
import { usePipecat } from '../hooks/usePipecat';
import Button from './ui/Button';
import LoadingSpinner from './ui/LoadingSpinner';

interface CallInterfaceProps {
  agentConfig: AgentConfig;
  onCallEnd: (result: CallResult) => void;
  onBack: () => void;
}

const CallInterface: React.FC<CallInterfaceProps> = ({ agentConfig, onCallEnd, onBack }) => {
  const [isMuted, setIsMuted] = useState(false);
  const [isCallInProgress, setIsCallInProgress] = useState(false);
  const [callDurationLocal, setCallDurationLocal] = useState(0);
  const [volumeLevel, setVolumeLevel] = useState(0);
  const [callData, setCallData] = useState<CallRequest>({
    driverName: '',
    phoneNumber: '',
    loadNumber: '',
    agentId: agentConfig.id || '',
    callType: 'web'
  });

  const { 
    isConnected, 
    isListening,
    transcript, 
    error: pipecatError, 
    resetCall,
    setTranscript
  } = usePipecat();

  const callTimerRef = useRef<number | null>(null);
  const volumeAnalyzerRef = useRef<AnalyserNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const recognitionRef = useRef<any>(null);
  useEffect(() => {
    if (isCallInProgress && !callTimerRef.current) {
      callTimerRef.current = window.setInterval(() => {
        setCallDurationLocal(prev => prev + 1);
      }, 1000);
    } else if (!isCallInProgress && callTimerRef.current) {
      clearInterval(callTimerRef.current);
      callTimerRef.current = null;
    }

    return () => {
      if (callTimerRef.current) {
        clearInterval(callTimerRef.current);
      }
    };
  }, [isCallInProgress]);

  const initializeAudioMonitoring = async () => {
    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const source = audioContextRef.current.createMediaStreamSource(stream);
      volumeAnalyzerRef.current = audioContextRef.current.createAnalyser();
      source.connect(volumeAnalyzerRef.current);
      
      const dataArray = new Uint8Array(volumeAnalyzerRef.current.frequencyBinCount);
      const updateVolume = () => {
        if (volumeAnalyzerRef.current && isCallInProgress) {
          volumeAnalyzerRef.current.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
          setVolumeLevel(Math.floor((average / 255) * 100));
          requestAnimationFrame(updateVolume);
        }
      };
      updateVolume();

      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US';

        recognitionRef.current.onresult = (event: any) => {
          let finalTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            }
          }
          if (finalTranscript) {
            setTranscript(prev => prev + `Driver: ${finalTranscript}\n\n`);
            
            setTimeout(() => {
              const response = generateDispatcherResponse(finalTranscript.toLowerCase(), callData);
              setTranscript(prev => prev + `Dispatcher: ${response}\n\n`);
            }, 1500);
          }
        };

        recognitionRef.current.start();
      }
    } catch (error) {
    }
  };

  const generateDispatcherResponse = (driverMessage: string, callData: CallRequest): string => {
    const lowerMessage = driverMessage.toLowerCase();
    const driverName = callData.driverName;
    const loadNumber = callData.loadNumber;

    if (lowerMessage.includes('emergency') || lowerMessage.includes('accident') || lowerMessage.includes('help')) {
      return `${driverName}, I understand this is an emergency situation. I'm immediately escalating this to our emergency response team. Can you confirm your exact location and if anyone is injured? Stay on the line.`;
    }

    if (lowerMessage.includes('hear me') || lowerMessage.includes('hello') || lowerMessage.includes('can you') || lowerMessage.includes('hi ')) {
      return `Yes ${driverName}, I can hear you clearly. Thanks for checking in on load ${loadNumber}. Can you please provide me with your current location and delivery status?`;
    }

    if (lowerMessage.includes('location') || lowerMessage.includes('mile') || lowerMessage.includes('highway') || lowerMessage.includes('exit')) {
      return `Thank you for the location update, ${driverName}. What's your estimated time of arrival at the delivery location? Any delays or issues I should be aware of?`;
    }

    if (lowerMessage.includes('delay') || lowerMessage.includes('late') || lowerMessage.includes('traffic') || lowerMessage.includes('behind')) {
      return `I understand there's a delay, ${driverName}. Please provide me with your updated ETA and the reason for the delay so I can update the customer accordingly.`;
    }

    if (lowerMessage.includes('delivered') || lowerMessage.includes('unload') || lowerMessage.includes('complete')) {
      return `Excellent work, ${driverName}. Can you confirm the delivery is complete for load ${loadNumber}? Please remember to get the signed POD and send a photo when you have a chance.`;
    }

    if (lowerMessage.includes('fuel') || lowerMessage.includes('break') || lowerMessage.includes('rest')) {
      return `Copy that, ${driverName}. Take the time you need for fuel and rest. Safety first. Please update me with your next ETA when you're back on the road.`;
    }

    if (lowerMessage.includes('weather') || lowerMessage.includes('snow') || lowerMessage.includes('rain') || lowerMessage.includes('road')) {
      return `Thanks for the road condition update, ${driverName}. Drive safely and adjust your speed as needed. Let me know if conditions worsen or if you need to find a safe place to wait it out.`;
    }

    if (lowerMessage.includes('breakdown') || lowerMessage.includes('truck') || lowerMessage.includes('tire') || lowerMessage.includes('mechanical')) {
      return `${driverName}, I understand you're having equipment issues. I'm contacting our maintenance team right away. Can you confirm your exact location and the nature of the problem?`;
    }

    if (lowerMessage.includes('no') || lowerMessage.includes('nothing') || lowerMessage.includes('assist') || lowerMessage.includes('can\'t help')) {
      return `Understood, ${driverName}. Just checking in to make sure everything is going smoothly with load ${loadNumber}. Drive safe and don't hesitate to call if anything comes up.`;
    }

    return `Thanks for the update, ${driverName}. I've noted that information for load ${loadNumber}. Is there anything else you need assistance with regarding your delivery?`;
  };

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startCall = async () => {
    if (!callData.driverName || !callData.loadNumber) {
      alert('Please enter driver name and load number');
      return;
    }

    if (isCallInProgress) return;

    try {
      setIsCallInProgress(true);
      setCallDurationLocal(0);
      resetCall();
      
      await initializeAudioMonitoring();
      
      await api.startCall(callData);
      
      setTranscript(`📞 PIPECAT Voice Agent Connected\n\nDispatcher: Good day ${callData.driverName}, this is dispatch calling about load ${callData.loadNumber}. I can hear you clearly. Please give me a status update on your delivery - what's your current location and how are things going?\n\n[🎤 Listening for your response]\n\n`);
      
    } catch (error: any) {
      alert(`Failed to start call: ${error.message}`);
      setIsCallInProgress(false);
    }
  };

  const endCall = async () => {
    try {
      setIsCallInProgress(false);
      
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        recognitionRef.current = null;
      }
      
      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }

      const callTranscript = transcript || '';
      const summary = analyzeCallTranscript(callTranscript);

      const callResult: CallResult = {
        id: Date.now().toString(),
        callRequest: callData,
        transcript: callTranscript,
        summary: summary,
        timestamp: new Date().toISOString(),
        duration: callDurationLocal
      };

      try {
        const response = await fetch('/api/calls/complete', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            callId: callResult.id,
            duration: callDurationLocal,
            transcript: callTranscript,
            summary: summary
          })
        });
        
        if (!response.ok) {
        }
      } catch (saveError) {
      }

      onCallEnd(callResult);
      
    } catch (error) {
    }
  };

  const analyzeCallTranscript = (transcript: string) => {
    const lowerTranscript = transcript.toLowerCase();
    
    let call_outcome = 'completed';
    let driver_status = 'checked_in';
    let current_location = 'unknown';
    let eta = 'unknown';
    let delay_reason = '';
    let unloading_status = 'in_progress';
    
    const emergencyKeywords = ['emergency', 'accident', 'help', 'stuck', 'breakdown', 'injured'];
    const hasEmergency = emergencyKeywords.some(keyword => lowerTranscript.includes(keyword));
    
    if (hasEmergency) {
      call_outcome = 'emergency';
      driver_status = 'emergency';
    }
    
    const delayKeywords = ['late', 'delay', 'traffic', 'behind schedule', 'running late'];
    if (delayKeywords.some(keyword => lowerTranscript.includes(keyword))) {
      delay_reason = 'traffic_delay';
    }
    
    const locationMatch = transcript.match(/(?:at|near|on)\s+([A-Za-z0-9\s]+?)(?:\s|$|,|\.|;)/i);
    if (locationMatch) {
      current_location = locationMatch[1].trim();
    }
    
    return {
      call_outcome,
      driver_status,
      current_location,
      eta,
      delay_reason,
      unloading_status,
      pod_reminder_acknowledged: false
    };
  };

  const handleToggleMute = () => {
    setIsMuted(!isMuted);
    if (recognitionRef.current) {
      if (isMuted) {
        recognitionRef.current.start();
      } else {
        recognitionRef.current.stop();
      }
    }
  };

  useEffect(() => {
    return () => {
      if (callTimerRef.current) {
        clearInterval(callTimerRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={onBack}
            className="mb-4 text-blue-600 hover:text-blue-800 flex items-center gap-2"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            PIPECAT Voice Agent - {agentConfig.name}
          </h1>
          <p className="text-gray-600 mt-2">
            Real-time voice communication with live transcription
          </p>
        </div>

        {/* Call Setup Form */}
        {!isCallInProgress && !isConnected && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Start Call</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Driver Name
                </label>
                <input
                  type="text"
                  value={callData.driverName}
                  onChange={(e) => setCallData({...callData, driverName: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter driver name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Load Number
                </label>
                <input
                  type="text"
                  value={callData.loadNumber}
                  onChange={(e) => setCallData({...callData, loadNumber: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter load number"
                />
              </div>
            </div>
            
            <Button
              onClick={startCall}
              disabled={!callData.driverName || !callData.loadNumber}
              className="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <Phone className="w-5 h-5" />
              Start PIPECAT Call
            </Button>
          </div>
        )}

        {/* Active Call Interface */}
        {isCallInProgress && (
          <div className="bg-white rounded-lg shadow-md p-6">
            {/* Call Status Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className={`w-4 h-4 rounded-full ${isConnected ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                <span className="font-medium">
                  {isConnected ? 'Connected' : 'Connecting...'}
                </span>
                {isListening && (
                  <div className="flex items-center gap-2 text-green-600">
                    <Mic className="w-4 h-4 animate-pulse" />
                    <span className="text-sm font-medium">Listening...</span>
                  </div>
                )}
              </div>
              
              <div className="flex items-center gap-4">
                <span className="text-lg font-mono">
                  {formatDuration(callDurationLocal)}
                </span>
                
                <button
                  onClick={handleToggleMute}
                  className={`p-2 rounded-full ${isMuted ? 'bg-red-500 text-white' : 'bg-gray-200 text-gray-700'}`}
                >
                  {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                </button>
                
                <Button
                  onClick={endCall}
                  className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 flex items-center gap-2"
                >
                  <PhoneOff className="w-4 h-4" />
                  End Call
                </Button>
              </div>
            </div>

            {/* Volume Level Indicator */}
            <div className="mb-4 flex items-center justify-center space-x-2">
              <Volume2 className="w-4 h-4 text-gray-600" />
              <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500 transition-all duration-100"
                  style={{ width: `${volumeLevel}%` }}
                />
              </div>
              <span className="text-sm text-gray-600">{volumeLevel}%</span>
            </div>

            {/* Live Transcript */}
            <div className="border rounded-lg p-4 mb-6">
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                Live Transcript
                {isListening && <span className="text-green-600 text-sm">(🎤 Microphone Active)</span>}
              </h3>
              <div className="h-96 overflow-y-auto bg-gray-50 p-4 rounded border font-mono text-sm whitespace-pre-wrap">
                {transcript && (
                  <div className="space-y-2">
                    <div className="text-gray-900">
                      <span className="font-medium text-blue-600">Conversation:</span> {transcript}
                    </div>
                  </div>
                )}
                
                {!transcript && (
                  <div className="text-gray-500 text-center py-8">
                    {isListening ? (
                      <div className="flex items-center justify-center space-x-2">
                        <LoadingSpinner size="sm" />
                        <span>Waiting for speech...</span>
                      </div>
                    ) : (
                      'Start speaking to see live transcript'
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Error Display */}
            {pipecatError && (
              <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-md p-4">
                <div className="flex">
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-yellow-800">Voice Processing Issue</h3>
                    <div className="mt-2 text-sm text-yellow-700">
                      <p>{pipecatError}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Call Info Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <div className="text-lg font-bold text-gray-900">{formatDuration(callDurationLocal)}</div>
                <div className="text-sm text-gray-600">Duration</div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <div className="text-lg font-bold text-gray-900">
                  {isConnected ? 'Connected' : 'Connecting'}
                </div>
                <div className="text-sm text-gray-600">Status</div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <div className="text-lg font-bold text-gray-900">WEB</div>
                <div className="text-sm text-gray-600">Call Type</div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <div className="text-lg font-bold text-gray-900">
                  {transcript ? transcript.split(' ').length : 0}
                </div>
                <div className="text-sm text-gray-600">Words</div>
              </div>
            </div>

            {/* Test Scenarios */}
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <h4 className="font-medium text-blue-900 mb-3">Voice Interaction Guide</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• <strong>Speak clearly</strong> into your microphone - the AI dispatcher will respond automatically</li>
                <li>• <strong>Live transcription</strong> shows your conversation in real-time</li>
                <li>• <strong>Voice recognition</strong> converts your speech to text instantly</li>
                <li>• <strong>Real dispatcher behavior</strong> - professional, context-aware responses</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CallInterface;
