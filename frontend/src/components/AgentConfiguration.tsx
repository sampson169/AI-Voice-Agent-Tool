import React, { useState } from 'react';
import { Save, Play } from 'lucide-react';
import type { AgentConfig } from '../types';

interface AgentConfigurationProps {
  onConfigSave: (config: AgentConfig) => void;
  onStartCall: () => void;
}

const AgentConfiguration: React.FC<AgentConfigurationProps> = ({ onConfigSave, onStartCall }) => {
  const [config, setConfig] = useState<AgentConfig>({
    name: 'Logistics Dispatch Agent',
    prompt: `You are a professional logistics dispatcher calling truck drivers for status updates on their loads. You must handle two main scenarios:

SCENARIO 1: End-to-End Driver Check-in
- Start with: "Hi [DRIVER_NAME], this is Dispatch with a check call on load [LOAD_NUMBER]. Can you give me an update on your status?"
- Based on their response, dynamically pivot your questioning
- If driving: Ask about location, ETA, any delays or issues
- If arrived: Ask about unloading status, dock assignment, any delays
- If delayed: Ask about reason, new ETA, current location
- Always end with POD (Proof of Delivery) reminder and safety message

SCENARIO 2: Emergency Protocol (CRITICAL)
- Listen for emergency trigger words: accident, breakdown, emergency, medical, help, urgent
- IMMEDIATELY abandon normal conversation flow when emergency detected
- Priority questions: "Is everyone safe? What's your exact location? What happened?"
- Gather: safety status, injury status, emergency location, load security
- End with: "I'm connecting you to a human dispatcher right now. Stay on the line."

CONVERSATION RULES:
- Use backchanneling and filler words for natural flow
- Handle interruptions gracefully
- For uncooperative drivers: probe 2-3 times then escalate
- For unclear responses: ask to repeat once, then continue
- For location conflicts: mention diplomatically without confrontation
- Stay professional but friendly throughout

Emergency triggers: accident, breakdown, emergency, medical, help, urgent, blowout, crash, collision, injury, hurt, stuck, disabled`,
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

  const loadScenarioTemplate = (scenarioType: 'check-in' | 'emergency') => {
    if (scenarioType === 'check-in') {
      setConfig({
        ...config,
        name: 'Logistics Driver Check-in Agent',
        prompt: `You are a professional logistics dispatcher calling truck drivers for routine status updates. Your goal is to conduct end-to-end check-in conversations that adapt based on the driver's current situation.

CONVERSATION FLOW:
1. GREETING: "Hi [DRIVER_NAME], this is Dispatch with a check call on load [LOAD_NUMBER]. Can you give me an update on your status?"

2. DYNAMIC BRANCHING based on response:
   - IF DRIVING: Ask about current location, ETA, any delays or issues
   - IF ARRIVED: Ask about unloading status, dock assignment, any delays
   - IF DELAYED: Ask about delay reason, new ETA, current location

3. FOLLOW-UP QUESTIONS:
   - For drivers: "What's your current location and estimated arrival time?"
   - For arrivals: "Are you unloading or waiting for a dock assignment?"
   - For delays: "What's causing the delay and when do you expect to arrive?"

4. WRAP UP: Always end with POD reminder and safety message

HANDLING DIFFICULT SITUATIONS:
- Uncooperative drivers: Probe 2-3 times, then politely end call
- Unclear responses: Ask for clarification once, then proceed
- One-word answers: "Can you give me a bit more detail about your current situation?"

CONVERSATION STYLE: Professional but friendly, use natural speech patterns with backchanneling.`,
      });
    } else if (scenarioType === 'emergency') {
      setConfig({
        ...config,
        name: 'Logistics Emergency Protocol Agent',
        prompt: `You are a logistics dispatcher trained in emergency response protocols. You must be ready to immediately switch from routine check-ins to emergency procedures when triggered.

EMERGENCY DETECTION:
Listen for: accident, breakdown, emergency, medical, help, urgent, blowout, crash, collision, injury, hurt, stuck, disabled

EMERGENCY PROTOCOL (IMMEDIATE PRIORITY SWITCH):
1. SAFETY FIRST: "I understand this is an emergency. Is everyone safe? Are there any injuries?"
2. LOCATION: "What's your exact location? Please give me the highway, mile marker, or nearest exit."
3. INCIDENT DETAILS: "What exactly happened? Was it an accident, breakdown, or medical emergency?"
4. ESCALATION: "I have all the details. I'm connecting you to a human dispatcher right now. Stay on the line."

STRUCTURED DATA TO COLLECT:
- Emergency type (Accident/Breakdown/Medical/Other)
- Safety status (everyone safe?)
- Injury status (any injuries?)
- Emergency location (exact position)
- Load security (is cargo secure?)

CRITICAL RULES:
- ABANDON normal conversation immediately when emergency detected
- Ask direct, clear questions in emergency situations
- Always escalate to human dispatcher
- Never provide medical or technical advice
- Maintain calm, professional tone while showing urgency

NORMAL CHECK-IN: If no emergency, proceed with standard status update flow.`,
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
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <button
                type="button"
                onClick={() => loadScenarioTemplate('check-in')}
                className="p-4 border border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 text-left transition-colors"
              >
                <h4 className="font-semibold text-gray-900 mb-2">Scenario 1: Driver Check-in</h4>
                <p className="text-sm text-gray-600">
                  End-to-end status updates with dynamic conversation flow based on driver's current situation (driving, arrived, delayed)
                </p>
              </button>
              <button
                type="button"
                onClick={() => loadScenarioTemplate('emergency')}
                className="p-4 border border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 text-left transition-colors"
              >
                <h4 className="font-semibold text-gray-900 mb-2">Scenario 2: Emergency Protocol</h4>
                <p className="text-sm text-gray-600">
                  Emergency detection and response with immediate protocol switch for accidents, breakdowns, and medical situations
                </p>
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