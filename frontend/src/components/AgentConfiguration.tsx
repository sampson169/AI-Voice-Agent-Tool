import React, { useState } from 'react';
import { Save, Play, Truck, AlertTriangle, Settings } from 'lucide-react';
import type { AgentConfig } from '../types';

interface AgentConfigurationProps {
  onConfigSave: (config: AgentConfig) => void;
  onStartCall: () => void;
}

const AgentConfiguration: React.FC<AgentConfigurationProps> = ({ onConfigSave, onStartCall }) => {
  const [config, setConfig] = useState<AgentConfig>({
    name: 'Logistics Dispatch Agent',
    scenarioType: 'general',
    prompt: `You are a professional logistics dispatcher calling truck drivers for status updates. You handle both routine check-ins and emergency situations with equal professionalism.

NORMAL CHECK-IN PROTOCOL:
1. Start with: "Hi [DRIVER_NAME], this is Dispatch with a check call on load [LOAD_NUMBER]. Can you give me an update on your status?"
2. Branch conversation based on their response:
   - Driving: Ask location, ETA, any issues
   - Arrived: Ask unloading status, dock details
   - Delayed: Ask delay reason, new ETA

EMERGENCY PROTOCOL (HIGHEST PRIORITY):
If you hear emergency words (accident, breakdown, emergency, medical, help, urgent), immediately:
1. "Is everyone safe? Any injuries?"
2. "What's your exact location?"
3. "What happened exactly?"
4. "I'm connecting you to a human dispatcher now."

CONVERSATION STYLE:
- Professional but friendly
- Use natural speech with backchanneling
- Handle interruptions gracefully
- Probe politely for unclear responses
- End with POD reminder and safety message`,
    voiceSettings: {
      voiceId: '11labs-Adrian',
      speed: 1.0,
      temperature: 0.7,
      backchanneling: true,
      fillerWords: true,
      interruptionSensitivity: 'medium',
    },
    emergencyPhrases: ['emergency', 'accident', 'breakdown', 'medical', 'help', 'urgent', 'blowout', 'crash', 'collision', 'injury', 'hurt', 'stuck', 'disabled'],
    structuredFields: [
      { key: 'call_outcome', label: 'Call Outcome', type: 'select', options: ['In-Transit Update', 'Arrival Confirmation', 'Emergency Escalation'] },
      { key: 'driver_status', label: 'Driver Status', type: 'select', options: ['Driving', 'Delayed', 'Arrived', 'Unloading'] },
      { key: 'current_location', label: 'Current Location', type: 'text' },
      { key: 'eta', label: 'ETA', type: 'text' },
      { key: 'delay_reason', label: 'Delay Reason', type: 'select', options: ['Heavy Traffic', 'Weather', 'Mechanical', 'Loading/Unloading', 'None'] },
      { key: 'unloading_status', label: 'Unloading Status', type: 'select', options: ['In Door', 'Waiting for Lumper', 'Detention', 'N/A'] },
      { key: 'pod_reminder_acknowledged', label: 'POD Reminder', type: 'boolean' },
      { key: 'emergency_type', label: 'Emergency Type', type: 'select', options: ['Accident', 'Breakdown', 'Medical', 'Other'] },
      { key: 'safety_status', label: 'Safety Status', type: 'text' },
      { key: 'injury_status', label: 'Injury Status', type: 'text' },
      { key: 'emergency_location', label: 'Emergency Location', type: 'text' },
      { key: 'load_secure', label: 'Load Secure', type: 'boolean' },
      { key: 'escalation_status', label: 'Escalation Status', type: 'text' },
    ],
  });

  const handleSave = () => {
    onConfigSave(config);
  };

  const loadScenarioTemplate = (scenarioType: 'driver_checkin' | 'emergency_protocol' | 'general') => {
    if (scenarioType === 'driver_checkin') {
      setConfig({
        ...config,
        name: 'Logistics Driver Check-in Agent',
        scenarioType: 'driver_checkin',
        prompt: `You are a professional logistics dispatcher calling truck drivers for routine status updates. Your goal is to conduct end-to-end check-in conversations that adapt dynamically based on the driver's current situation.

CONVERSATION FLOW:
1. GREETING: "Hi [DRIVER_NAME], this is Dispatch with a check call on load [LOAD_NUMBER]. Can you give me an update on your status?"

2. DYNAMIC BRANCHING based on driver response:
   - IF DRIVING: Ask about current location, ETA, any delays or issues
   - IF ARRIVED: Ask about unloading status, dock assignment, any delays  
   - IF DELAYED: Ask about delay reason, new ETA, current location

3. FOLLOW-UP QUESTIONS (adapt based on their answers):
   - For drivers: "What's your current location and estimated arrival time?"
   - For arrivals: "Are you unloading or waiting for a dock assignment? What door are you in?"
   - For delays: "What's causing the delay and when do you expect to arrive?"

4. WRAP UP: Always end with POD reminder and safety message

HANDLING DIFFICULT SITUATIONS:
- Uncooperative drivers: Probe 2-3 times with rephrased questions, then politely end call
- Unclear responses: Ask for clarification once: "Could you give me a bit more detail about your current situation?"
- One-word answers: "I want to make sure I have all the details. Can you tell me more about [specific topic]?"
- Noisy environment: "I'm having trouble hearing you clearly. Could you please repeat that?"

CONVERSATION STYLE: 
- Professional but friendly and conversational
- Use natural speech patterns with backchanneling ("uh-huh", "okay", "I see")
- Allow for interruptions and respond naturally
- Show empathy for delays or difficulties

DATA TO COLLECT:
- Driver status (Driving/Delayed/Arrived/Unloading)
- Current location (highway, mile marker, city)
- ETA (estimated arrival time)
- Delay reason (if applicable)
- Unloading status (if arrived)
- POD reminder acknowledgment

EMERGENCY PROTOCOL: 
If you detect emergency words (accident, breakdown, emergency, medical, help, urgent), IMMEDIATELY switch to emergency protocol and ask about safety first.`,
        structuredFields: [
          { key: 'call_outcome', label: 'Call Outcome', type: 'select', options: ['In-Transit Update', 'Arrival Confirmation'] },
          { key: 'driver_status', label: 'Driver Status', type: 'select', options: ['Driving', 'Delayed', 'Arrived', 'Unloading'] },
          { key: 'current_location', label: 'Current Location', type: 'text' },
          { key: 'eta', label: 'ETA', type: 'text' },
          { key: 'delay_reason', label: 'Delay Reason', type: 'select', options: ['Heavy Traffic', 'Weather', 'Mechanical', 'Loading/Unloading', 'None'] },
          { key: 'unloading_status', label: 'Unloading Status', type: 'select', options: ['In Door', 'Waiting for Lumper', 'Detention', 'N/A'] },
          { key: 'pod_reminder_acknowledged', label: 'POD Reminder', type: 'boolean' }
        ]
      });
    } else if (scenarioType === 'emergency_protocol') {
      setConfig({
        ...config,
        name: 'Logistics Emergency Protocol Agent',
        scenarioType: 'emergency_protocol',
        prompt: `You are a logistics dispatcher trained in emergency response protocols. You must be ready to immediately switch from routine check-ins to emergency procedures when triggered.

EMERGENCY DETECTION:
Listen for: accident, breakdown, emergency, medical, help, urgent, blowout, crash, collision, injury, hurt, stuck, disabled, broke down, can't move, need help, pulled over

EMERGENCY PROTOCOL (IMMEDIATE PRIORITY SWITCH):
When emergency is detected, ABANDON all normal conversation flow and follow this exact sequence:

1. SAFETY ASSESSMENT: "I understand this is an emergency. Is everyone safe? Are there any injuries that need immediate medical attention?"
2. LOCATION GATHERING: "What's your exact location? Please give me the highway, mile marker, or nearest exit."
3. INCIDENT DETAILS: "What exactly happened? Was it an accident, breakdown, or medical emergency?"
4. LOAD SECURITY: "Is your load secure? Any cargo damage or spills I should know about?"
5. ESCALATION: "I have all the emergency details. I'm connecting you to a human dispatcher right now. Stay on the line and they'll be with you immediately."

STRUCTURED DATA TO COLLECT:
- Emergency type (Accident/Breakdown/Medical/Other)
- Safety status (confirmed everyone safe?)
- Injury status (any injuries reported?)
- Emergency location (exact highway position)
- Load security (cargo secure or damaged?)

CRITICAL RULES:
- ABANDON normal conversation immediately when emergency detected
- Ask direct, clear questions - no small talk during emergencies
- Always escalate to human dispatcher - never try to solve emergencies yourself
- Never provide medical or technical repair advice
- Maintain calm, professional tone while showing appropriate urgency
- If driver is incoherent or very distressed, immediately escalate

NORMAL OPERATIONS: 
If no emergency is detected, proceed with standard driver check-in procedures asking about status, location, and ETA.`,
        structuredFields: [
          { key: 'call_outcome', label: 'Call Outcome', type: 'select', options: ['Emergency Escalation'] },
          { key: 'emergency_type', label: 'Emergency Type', type: 'select', options: ['Accident', 'Breakdown', 'Medical', 'Other'] },
          { key: 'safety_status', label: 'Safety Status', type: 'text' },
          { key: 'injury_status', label: 'Injury Status', type: 'text' },
          { key: 'emergency_location', label: 'Emergency Location', type: 'text' },
          { key: 'load_secure', label: 'Load Secure', type: 'boolean' },
          { key: 'escalation_status', label: 'Escalation Status', type: 'text' }
        ]
      });
    } else if (scenarioType === 'general') {
      setConfig({
        ...config,
        name: 'General Logistics Dispatcher',
        scenarioType: 'general',
        prompt: `You are a professional logistics dispatcher calling truck drivers for status updates. You handle both routine check-ins and emergency situations with equal professionalism.

NORMAL CHECK-IN PROTOCOL:
1. Start with: "Hi [DRIVER_NAME], this is Dispatch with a check call on load [LOAD_NUMBER]. Can you give me an update on your status?"
2. Branch conversation based on their response:
   - Driving: Ask location, ETA, any issues
   - Arrived: Ask unloading status, dock details
   - Delayed: Ask delay reason, new ETA

EMERGENCY PROTOCOL (HIGHEST PRIORITY):
If you hear emergency words (accident, breakdown, emergency, medical, help, urgent), immediately:
1. "Is everyone safe? Any injuries?"
2. "What's your exact location?"
3. "What happened exactly?"
4. "I'm connecting you to a human dispatcher now."

CONVERSATION STYLE:
- Professional but friendly
- Use natural speech with backchanneling ("uh-huh", "okay", "I see")
- Handle interruptions gracefully
- Probe politely for unclear responses
- End with POD reminder and safety message

OPTIMAL VOICE SETTINGS:
- Use backchanneling and filler words for natural flow
- Medium interruption sensitivity for realistic conversations
- Professional but warm tone throughout

This configuration handles both routine logistics check-ins and emergency situations seamlessly.`,
        structuredFields: [
          { key: 'call_outcome', label: 'Call Outcome', type: 'select', options: ['In-Transit Update', 'Arrival Confirmation', 'Emergency Escalation'] },
          { key: 'driver_status', label: 'Driver Status', type: 'select', options: ['Driving', 'Delayed', 'Arrived', 'Unloading'] },
          { key: 'current_location', label: 'Current Location', type: 'text' },
          { key: 'eta', label: 'ETA', type: 'text' },
          { key: 'delay_reason', label: 'Delay Reason', type: 'select', options: ['Heavy Traffic', 'Weather', 'Mechanical', 'Loading/Unloading', 'Fuel', 'DOT/Legal', 'Other', 'None'] },
          { key: 'unloading_status', label: 'Unloading Status', type: 'select', options: ['In Door', 'Waiting for Lumper', 'Detention', 'N/A'] },
          { key: 'pod_reminder_acknowledged', label: 'POD Reminder', type: 'boolean' },
          { key: 'emergency_type', label: 'Emergency Type', type: 'select', options: ['Accident', 'Breakdown', 'Medical', 'Other'] },
          { key: 'safety_status', label: 'Safety Status', type: 'text' },
          { key: 'injury_status', label: 'Injury Status', type: 'text' },
          { key: 'emergency_location', label: 'Emergency Location', type: 'text' },
          { key: 'load_secure', label: 'Load Secure', type: 'boolean' },
          { key: 'escalation_status', label: 'Escalation Status', type: 'text' }
        ]
      });
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Agent Configuration</h2>
        
        <div className="space-y-6">
          {/* Agent Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Agent Name
            </label>
            <input
              type="text"
              value={config.name}
              onChange={(e) => setConfig({ ...config, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Enter agent name"
            />
          </div>

          {/* Prompt Configuration */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Conversation Prompt
            </label>
            <textarea
              value={config.prompt}
              onChange={(e) => setConfig({ ...config, prompt: e.target.value })}
              rows={8}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono text-sm"
              placeholder="Define the agent's conversation logic..."
            />
          </div>

          {/* Voice Settings */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Voice Speed
              </label>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={config.voiceSettings.speed}
                onChange={(e) => setConfig({
                  ...config,
                  voiceSettings: { ...config.voiceSettings, speed: parseFloat(e.target.value) }
                })}
                className="w-full"
              />
              <span className="text-sm text-gray-600">{config.voiceSettings.speed}x</span>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Temperature (Creativity)
              </label>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.1"
                value={config.voiceSettings.temperature}
                onChange={(e) => setConfig({
                  ...config,
                  voiceSettings: { ...config.voiceSettings, temperature: parseFloat(e.target.value) }
                })}
                className="w-full"
              />
              <span className="text-sm text-gray-600">{config.voiceSettings.temperature}</span>
            </div>
          </div>

          {/* Advanced Settings */}
          <div className="grid grid-cols-3 gap-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={config.voiceSettings.backchanneling}
                onChange={(e) => setConfig({
                  ...config,
                  voiceSettings: { ...config.voiceSettings, backchanneling: e.target.checked }
                })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700">Backchanneling</span>
            </label>

            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={config.voiceSettings.fillerWords}
                onChange={(e) => setConfig({
                  ...config,
                  voiceSettings: { ...config.voiceSettings, fillerWords: e.target.checked }
                })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700">Filler Words</span>
            </label>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Interruption Sensitivity
              </label>
              <select
                value={config.voiceSettings.interruptionSensitivity}
                onChange={(e) => setConfig({
                  ...config,
                  voiceSettings: { 
                    ...config.voiceSettings, 
                    interruptionSensitivity: e.target.value as 'low' | 'medium' | 'high' 
                  }
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>

          {/* Scenario Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Select Logistics Scenario Template
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <button
                type="button"
                onClick={() => loadScenarioTemplate('driver_checkin')}
                className="p-4 border border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 text-left transition-colors"
              >
                <div className="flex items-start space-x-3">
                  <Truck className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Scenario 1: Driver Check-in</h4>
                    <p className="text-sm text-gray-600">
                      End-to-end status updates with dynamic conversation flow based on driver's current situation (driving, arrived, delayed)
                    </p>
                  </div>
                </div>
              </button>
              
              <button
                type="button"
                onClick={() => loadScenarioTemplate('emergency_protocol')}
                className="p-4 border border-gray-300 rounded-lg hover:border-red-500 hover:bg-red-50 text-left transition-colors"
              >
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Scenario 2: Emergency Protocol</h4>
                    <p className="text-sm text-gray-600">
                      Emergency detection and response with immediate protocol switch for accidents, breakdowns, and medical situations
                    </p>
                  </div>
                </div>
              </button>
              
              <button
                type="button"
                onClick={() => loadScenarioTemplate('general')}
                className="p-4 border border-gray-300 rounded-lg hover:border-green-500 hover:bg-green-50 text-left transition-colors"
              >
                <div className="flex items-start space-x-3">
                  <Settings className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">General Dispatcher</h4>
                    <p className="text-sm text-gray-600">
                      Comprehensive agent that handles both routine check-ins and emergency situations seamlessly
                    </p>
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Emergency Phrases */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Emergency Trigger Phrases
            </label>
            <textarea
              value={config.emergencyPhrases.join(', ')}
              onChange={(e) => setConfig({
                ...config,
                emergencyPhrases: e.target.value.split(',').map(phrase => phrase.trim()).filter(Boolean)
              })}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="emergency, accident, breakdown, medical..."
            />
            <p className="text-sm text-gray-500 mt-1">Separate phrases with commas</p>
          </div>
        </div>

        <div className="flex justify-end space-x-4 mt-8 pt-6 border-t">
          <button
            onClick={handleSave}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <Save className="h-4 w-4" />
            <span>Save Configuration</span>
          </button>

          <button
            onClick={onStartCall}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <Play className="h-4 w-4" />
            <span>Start Test Call</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AgentConfiguration;