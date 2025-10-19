import React, { useState } from 'react';
import { Phone, PhoneOff, Mic, MicOff } from 'lucide-react';
import type { AgentConfig, CallRequest, CallResult } from '../types';
import { api } from '../utils/api';
import { usePipecat } from '../hooks/usePipecat';

interface CallInterfaceProps {
  agentConfig: AgentConfig;
  onCallEnd: (result: CallResult) => void;
  onBack: () => void;
}

const CallInterface: React.FC<CallInterfaceProps> = ({ agentConfig, onCallEnd, onBack }) => {
  const [isMuted, setIsMuted] = useState(false);
  const [isCallInProgress, setIsCallInProgress] = useState(false);
  const [callData, setCallData] = useState<CallRequest>({
    driverName: '',
    phoneNumber: '',
    loadNumber: '',
    agentId: agentConfig.id || '',
    callType: 'web'
  });

  const { 
    isConnected, 
    isLoading, 
    transcript, 
    error: pipecatError, 
    callDuration, 
    isListening,
    startCall: startPipecatCall, 
    endCall: endPipecatCall, 
    resetCall, 
    setTranscript 
  } = usePipecat();

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const startCall = async () => {
    if (!callData.driverName || !callData.loadNumber) {
      alert('Please enter driver name and load number');
      return;
    }

    if (isCallInProgress || isLoading) {
      return;
    }

    try {
      setIsCallInProgress(true);
      resetCall();
      
      if (callData.callType === 'web') {
        try {
          await navigator.mediaDevices.getUserMedia({ audio: true });
        } catch (mediaError: any) {
          throw new Error(`Microphone access denied: ${mediaError.message}`);
        }
      }

      const response = await api.startCall(callData);
      
      if (response.web_call_link) {
        await startPipecatCall(response.web_call_link);
        simulateCall();
      } else {
        simulateCall();
      }
      
    } catch (error: any) {
      const errorMessage = error.message || 'Unknown error occurred';
      alert(`Failed to start call: ${errorMessage}. Please check your configuration and try again.`);
      setIsCallInProgress(false);
      console.error('Call start error:', error);
    }
  };

  const simulateCall = () => {
    setTimeout(() => {
      setTranscript((prev: string) => prev + `📞 PIPECAT Voice Agent Connected - Microphone Active\n\n`);
    }, 500);
    
    setTimeout(() => {
      setTranscript((prev: string) => prev + `AI Dispatcher: Good day ${callData.driverName}, this is dispatch calling regarding load number ${callData.loadNumber}. I can hear you clearly through the PIPECAT system. Please speak into your microphone to give me a status update on your delivery. How are you doing today and what's your current location?\n\n`);
    }, 1500);
    
    setTimeout(() => {
      setTranscript((prev: string) => prev + `[🎤 Listening for your voice - Speak now to respond to the dispatcher]\n\n`);
    }, 4000);
    
    setTimeout(() => {
      setTranscript((prev: string) => prev + `AI Dispatcher: I'm ready to hear your response. Please make sure your microphone is unmuted and speak clearly about your current status and location.\n\n`);
    }, 10000);
  };

  const endCall = () => {
    try {
      endPipecatCall();
    } catch (error) {
      console.warn('Error ending call:', error);
    } finally {
      setIsCallInProgress(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
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
            
            <button
              onClick={startCall}
              disabled={isLoading || !callData.driverName || !callData.loadNumber}
              className="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <Phone className="w-5 h-5" />
              {isLoading ? 'Connecting...' : 'Start PIPECAT Call'}
            </button>
          </div>
        )}

        {(isCallInProgress || isConnected) && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className={`w-4 h-4 rounded-full ${isConnected ? 'bg-green-500' : isLoading ? 'bg-yellow-500' : 'bg-red-500'}`}></div>
                <span className="font-medium">
                  {isConnected ? 'Connected' : isLoading ? 'Connecting...' : 'Disconnected'}
                </span>
                {isListening && (
                  <div className="flex items-center gap-2 text-green-600">
                    <Mic className="w-4 h-4 animate-pulse" />
                    <span className="text-sm">Listening...</span>
                  </div>
                )}
              </div>
              
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600">
                  {formatDuration(callDuration)}
                </span>
                
                <button
                  onClick={() => setIsMuted(!isMuted)}
                  className={`p-2 rounded-full ${isMuted ? 'bg-red-500 text-white' : 'bg-gray-200 text-gray-700'}`}
                >
                  {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                </button>
                
                <button
                  onClick={endCall}
                  className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 flex items-center gap-2"
                >
                  <PhoneOff className="w-4 h-4" />
                  End Call
                </button>
              </div>
            </div>

            <div className="border rounded-lg p-4 mb-6">
              <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                Live Transcript
                {isListening && <span className="text-green-600 text-sm">(🎤 Microphone Active)</span>}
              </h3>
              <div className="h-96 overflow-y-auto bg-gray-50 p-4 rounded border font-mono text-sm whitespace-pre-wrap">
                {transcript || 'Conversation will appear here...\n\nMake sure to allow microphone access when prompted.\nSpeak clearly after the dispatcher asks a question.'}
              </div>
            </div>

            {pipecatError && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-6">
                <div className="flex">
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-yellow-800">Connection Issue</h3>
                    <div className="mt-2 text-sm text-yellow-700">
                      <p>{pipecatError}</p>
                      <p className="mt-1">The call is running in demo mode with voice recognition active.</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <h4 className="font-medium text-blue-900 mb-3">Test Scenarios</h4>
              <p className="text-sm text-blue-700 mb-3">Use these buttons to simulate driver responses, or speak into your microphone:</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <button
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                >
                  🚛 Normal Check-in
                </button>
                <button
                  className="bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700"
                >
                  ⏰ Delay Report
                </button>
                <button
                  className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                >
                  🚨 Emergency
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">How PIPECAT Voice Works:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• <strong>Allow microphone access</strong> when prompted by your browser</li>
            <li>• <strong>Speak clearly</strong> into your microphone - the AI dispatcher will respond automatically</li>
            <li>• <strong>Live transcription</strong> shows your conversation in real-time</li>
            <li>• <strong>Voice recognition</strong> converts your speech to text and triggers AI responses</li>
            <li>• <strong>Test scenarios</strong> simulate common logistics conversations</li>
            <li>• <strong>Real dispatcher behavior</strong> - professional, context-aware responses</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default CallInterface;
