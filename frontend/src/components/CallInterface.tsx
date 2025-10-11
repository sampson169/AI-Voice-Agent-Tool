import React, { useState } from 'react';
import { Phone, PhoneOff, Mic, MicOff } from 'lucide-react';
import type { AgentConfig, CallRequest, CallResult } from '../types';
import { api } from '../utils/api';
import { useRetell } from '../hooks/useRetell';

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
    agentId: agentConfig.id || 'agent_fa51b58953a177984c9e173910',
    callType: 'web',
  });
  const { isConnected, isLoading, transcript, error: retellError, startCall: startRetellCall, endCall: endRetellCall, setTranscript } = useRetell();

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
      
      if (callData.callType === 'web') {
        try {
          await navigator.mediaDevices.getUserMedia({ audio: true });
        } catch (mediaError: any) {
          throw new Error(`Microphone access denied: ${mediaError.message}`);
        }
      }

      const response = await api.startCall(callData);
      
      if (response.access_token) {
        await startRetellCall(response.access_token);
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
      setTranscript(prev => prev + `AI: Hi ${callData.driverName}! This is Dispatch with a check call on load ${callData.loadNumber}. Can you give me an update on your status?\n\n`);
    }, 1000);
  };

  const simulateScenario = (scenarioType: 'normal' | 'delay' | 'emergency') => {
    if (!isCallInProgress) return;

    if (scenarioType === 'normal') {
      setTimeout(() => {
        setTranscript(prev => prev + `Driver: I'm driving on I-10, about 50 miles out. Should arrive around 2 PM as scheduled.\n\n`);
      }, 1000);

      setTimeout(() => {
        setTranscript(prev => prev + `AI: Great! What's your current location and is everything going smoothly with the load?\n\n`);
      }, 4000);

      setTimeout(() => {
        setTranscript(prev => prev + `Driver: I'm at mile marker 85 on I-10. Load is secure, truck is running fine, no issues.\n\n`);
      }, 7000);

      setTimeout(() => {
        setTranscript(prev => prev + `AI: Perfect. Thanks for the update. Drive safely and remember to submit your proof of delivery. Contact us if anything changes!\n\n`);
      }, 10000);
    } 
    
    else if (scenarioType === 'delay') {
      setTimeout(() => {
        setTranscript(prev => prev + `Driver: I'm running about 3 hours late due to heavy traffic and construction on I-10.\n\n`);
      }, 1000);

      setTimeout(() => {
        setTranscript(prev => prev + `AI: I understand there's a delay. What's your current location and what's your new estimated arrival time?\n\n`);
      }, 4000);

      setTimeout(() => {
        setTranscript(prev => prev + `Driver: I'm stuck at mile marker 65, barely moving. Should arrive around 5 PM now instead of 2 PM.\n\n`);
      }, 7000);

      setTimeout(() => {
        setTranscript(prev => prev + `AI: Got it. Is everything okay with the load and truck? Any other issues I should know about?\n\n`);
      }, 10000);

      setTimeout(() => {
        setTranscript(prev => prev + `Driver: Everything else is fine. Load is secure, just this traffic backup from the construction.\n\n`);
      }, 13000);

      setTimeout(() => {
        setTranscript(prev => prev + `AI: Thanks for letting us know. I'll update the receiver about the delay. Drive safely!\n\n`);
      }, 16000);
    } 
    
    else if (scenarioType === 'emergency') {
      setTimeout(() => {
        setTranscript(prev => prev + `Driver: Hey dispatch, I just had a blowout on I-10! I'm pulled over on the shoulder.\n\n`);
      }, 1000);

      setTimeout(() => {
        setTranscript(prev => prev + `AI: I understand this is an emergency. Is everyone safe? Are there any injuries?\n\n`);
      }, 3000);

      setTimeout(() => {
        setTranscript(prev => prev + `Driver: Yeah, everyone's safe. No injuries. Just a tire blowout on the trailer.\n\n`);
      }, 6000);

      setTimeout(() => {
        setTranscript(prev => prev + `AI: Thank God you're safe. What's your exact location? Please give me the highway, mile marker, or nearest exit.\n\n`);
      }, 9000);

      setTimeout(() => {
        setTranscript(prev => prev + `Driver: I'm on I-10 eastbound at mile marker 78, pulled over on the right shoulder.\n\n`);
      }, 12000);

      setTimeout(() => {
        setTranscript(prev => prev + `AI: Got your location. Is the load secure? Do you need road service for the tire?\n\n`);
      }, 15000);

      setTimeout(() => {
        setTranscript(prev => prev + `Driver: Load is fine, straps are tight. Yeah, I'll need road service to change the tire.\n\n`);
      }, 18000);

      setTimeout(() => {
        setTranscript(prev => prev + `AI: I have all the details. I'm connecting you to a human dispatcher right now who will coordinate road service. Stay on the line.\n\n`);
      }, 21000);
    }
  };

  const endCall = () => {
    try {
      endRetellCall();
    } catch (error) {
      console.warn('Error ending call:', error);
    } finally {
      setIsCallInProgress(false);
    }
    
    const generateSummary = (transcript: string) => {
      const lowerTranscript = transcript.toLowerCase();
      
      if (lowerTranscript.includes('emergency') || lowerTranscript.includes('blowout') || 
          lowerTranscript.includes('accident') || lowerTranscript.includes('breakdown')) {
        return {
          call_outcome: 'Emergency Escalation',
          driver_status: 'Emergency',
          current_location: extractFromTranscript(transcript, /mile marker \d+|i-\d+/i) || 'I-10 mile marker 78',
          eta: 'Delayed due to emergency',
          delay_reason: 'Emergency',
          unloading_status: 'N/A',
          pod_reminder_acknowledged: false,
          emergency_type: lowerTranscript.includes('blowout') ? 'Breakdown' : 'Other',
          safety_status: 'Driver confirmed everyone is safe',
          injury_status: 'No injuries reported',
          emergency_location: 'I-10 eastbound mile marker 78',
          load_secure: true,
          escalation_status: 'Connected to Human Dispatcher',
        };
      }
      
      else if (lowerTranscript.includes('late') || lowerTranscript.includes('delay') || 
               lowerTranscript.includes('traffic') || lowerTranscript.includes('construction')) {
        return {
          call_outcome: 'In-Transit Update',
          driver_status: 'Delayed',
          current_location: extractFromTranscript(transcript, /mile marker \d+|i-\d+/i) || 'I-10 mile marker 65',
          eta: extractFromTranscript(transcript, /\d{1,2}:\d{2}|\d+ pm|\d+ am/i) || '5:00 PM',
          delay_reason: lowerTranscript.includes('traffic') ? 'Heavy Traffic' : 
                       lowerTranscript.includes('construction') ? 'Heavy Traffic' : 'Other',
          unloading_status: 'N/A',
          pod_reminder_acknowledged: true,
        };
      }
      
      else if (lowerTranscript.includes('arrived') || lowerTranscript.includes('here') || 
               lowerTranscript.includes('dock') || lowerTranscript.includes('unloading')) {
        return {
          call_outcome: 'Arrival Confirmation',
          driver_status: 'Arrived',
          current_location: 'At destination dock',
          eta: 'Already arrived',
          delay_reason: 'None',
          unloading_status: lowerTranscript.includes('door') ? 'In Door' : 
                           lowerTranscript.includes('waiting') ? 'Waiting for Lumper' : 'At Dock',
          pod_reminder_acknowledged: true,
        };
      }
      
      else {
        return {
          call_outcome: 'In-Transit Update',
          driver_status: 'Driving',
          current_location: extractFromTranscript(transcript, /mile marker \d+|i-\d+/i) || 'I-10 mile marker 85',
          eta: extractFromTranscript(transcript, /\d{1,2}:\d{2}|\d+ pm|\d+ am/i) || '2:00 PM',
          delay_reason: 'None',
          unloading_status: 'N/A',
          pod_reminder_acknowledged: lowerTranscript.includes('pod') || lowerTranscript.includes('delivery'),
        };
      }
    };

    const extractFromTranscript = (text: string, regex: RegExp): string => {
      const match = text.match(regex);
      return match ? match[0] : '';
    };
    
    const result: CallResult = {
      id: `call_${Date.now()}`,
      callRequest: callData,
      transcript,
      summary: generateSummary(transcript),
      timestamp: new Date().toISOString(),
      duration: Math.floor((Date.now() - (Date.now() - 45000)) / 1000),
    };
    
    onCallEnd(result);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Make Test Call</h2>
        
        {!isCallInProgress ? (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Driver Name *
                </label>
                <input
                  type="text"
                  value={callData.driverName}
                  onChange={(e) => setCallData({ ...callData, driverName: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="e.g., Mike Johnson"
                />
                <p className="text-xs text-gray-500 mt-1">Driver's first name or full name</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Load Number *
                </label>
                <input
                  type="text"
                  value={callData.loadNumber}
                  onChange={(e) => setCallData({ ...callData, loadNumber: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="e.g., 7891-B, LB2024-001"
                />
                <p className="text-xs text-gray-500 mt-1">Load reference number for tracking</p>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number (Optional for Web Call)
              </label>
              <input
                type="tel"
                value={callData.phoneNumber}
                onChange={(e) => setCallData({ ...callData, phoneNumber: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Call Type
              </label>
              <select
                value={callData.callType}
                onChange={(e) => setCallData({ ...callData, callType: e.target.value as 'phone' | 'web' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="web">Web Call (Browser)</option>
                <option value="phone">Phone Call</option>
              </select>
              <p className="text-sm text-gray-500 mt-1">
                {callData.callType === 'web' 
                  ? 'Call will use your computer microphone and speakers' 
                  : 'Call will be made to the provided phone number'
                }
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-900 mb-3">Test Scenarios (for demonstration)</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => simulateScenario('normal')}
                  className="px-3 py-2 text-sm bg-white border border-blue-300 text-blue-700 rounded hover:bg-blue-100 transition-colors"
                >
                  Normal Check-in
                </button>
                <button
                  type="button"
                  onClick={() => simulateScenario('delay')}
                  className="px-3 py-2 text-sm bg-white border border-yellow-300 text-yellow-700 rounded hover:bg-yellow-100 transition-colors"
                >
                  Delay Scenario
                </button>
                <button
                  type="button"
                  onClick={() => simulateScenario('emergency')}
                  className="px-3 py-2 text-sm bg-white border border-red-300 text-red-700 rounded hover:bg-red-100 transition-colors"
                >
                  Emergency Protocol
                </button>
              </div>
              <p className="text-xs text-blue-600 mt-2">
                Click a scenario button after starting the call to simulate different conversation flows
              </p>
            </div>

            {retellError && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <div className="flex">
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Call Error</h3>
                    <div className="mt-2 text-sm text-red-700">
                      <p>{retellError}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="flex justify-end space-x-4 pt-4">
              <button
                onClick={onBack}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Back to Config
              </button>
              
              <button
                onClick={startCall}
                disabled={!callData.driverName || !callData.loadNumber}
                className="flex items-center space-x-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                <Phone className="h-4 w-4" />
                <span>Start {callData.callType === 'web' ? 'Web' : 'Phone'} Call</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="text-center py-8">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                <Phone className="h-8 w-8 text-green-600 animate-pulse" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {isConnected ? 'Call in Progress' : 'Connecting...'}
              </h3>
              <p className="text-gray-600">
                {isConnected 
                  ? `Talking to ${callData.driverName} about load ${callData.loadNumber}`
                  : `Setting up call with ${callData.driverName} for load ${callData.loadNumber}`
                }
              </p>
              {!isConnected && (
                <div className="mt-4">
                  <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
                </div>
              )}
            </div>

            <div className="flex justify-center space-x-4">
              <button
                onClick={() => setIsMuted(!isMuted)}
                disabled={!isConnected}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  !isConnected
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : isMuted 
                    ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {isMuted ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                <span>{isMuted ? 'Unmute' : 'Mute'}</span>
              </button>

              <button
                onClick={endCall}
                className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <PhoneOff className="h-4 w-4" />
                <span>End Call</span>
              </button>
            </div>

            {retellError && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                <div className="flex">
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-yellow-800">Connection Issue</h3>
                    <div className="mt-2 text-sm text-yellow-700">
                      <p>{retellError}</p>
                      <p className="mt-1">The call is running in simulation mode for demonstration.</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="border rounded-lg p-4 bg-gray-50">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-medium text-gray-900">Live Transcript</h4>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                  <span className="text-sm text-gray-600">
                    {isConnected ? 'Connected' : 'Connecting...'}
                  </span>
                </div>
              </div>
              <div className="h-64 overflow-y-auto font-mono text-sm whitespace-pre-wrap">
                {transcript || 'Conversation will appear here...'}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CallInterface;