import React, { useState } from 'react';
import { Save, Play, Truck, AlertTriangle, Settings } from 'lucide-react';
import type { AgentConfig } from '../types';
import { PROMPT_TEMPLATES, SCENARIO_DESCRIPTIONS, DEFAULT_EMERGENCY_PHRASES } from '../constants/promptTemplates';
import { SCENARIO_FIELDS } from '../constants/fieldDefinitions';
import { MESSAGES, LABELS, PLACEHOLDERS } from '../constants/messages';
import { useError } from '../hooks/useError';
import Button from './ui/Button';
import { TextField, TextArea } from './ui/FormFields';
import ScenarioCard from './ui/ScenarioCard';
import ErrorDisplay from './ui/ErrorDisplay';
import { createError } from '../utils/errorHandling';

interface AgentConfigurationProps {
  onConfigSave: (config: AgentConfig) => void;
  onStartCall: () => void;
}

const AgentConfiguration: React.FC<AgentConfigurationProps> = ({ onConfigSave, onStartCall }) => {
  const { errorState, showError, clearError } = useError();

  const createMutableFields = (fields: readonly any[]) =>
    fields.map(field => ({
      ...field,
      options: field.options ? [...field.options] : undefined
    }));

  const [config, setConfig] = useState<AgentConfig>({
    name: 'Logistics Dispatch Agent',
    scenarioType: 'general',
    prompt: PROMPT_TEMPLATES.GENERAL_DISPATCHER,
    voiceSettings: {
      voiceId: '11labs-Adrian',
      speed: 1.0,
      temperature: 0.7,
      backchanneling: true,
      fillerWords: true,
      interruptionSensitivity: 'medium',
    },
    emergencyPhrases: [...DEFAULT_EMERGENCY_PHRASES],
    structuredFields: createMutableFields(SCENARIO_FIELDS.GENERAL),
  });

  const handleSave = () => {
    try {
      onConfigSave(config);
    } catch (error) {
      showError(createError(
        'INVALID_CONFIGURATION',
        'Failed to save configuration',
        'Unable to save the agent configuration. Please check your settings and try again.',
        'medium'
      ));
    }
  };

  const loadScenarioTemplate = (scenarioType: 'driver_checkin' | 'emergency_protocol' | 'general') => {
    try {
      if (scenarioType === 'driver_checkin') {
        setConfig({
          ...config,
          name: 'Logistics Driver Check-in Agent',
          scenarioType: 'driver_checkin',
          prompt: PROMPT_TEMPLATES.DRIVER_CHECKIN,
          structuredFields: createMutableFields(SCENARIO_FIELDS.DRIVER_CHECKIN)
        });
      } else if (scenarioType === 'emergency_protocol') {
        setConfig({
          ...config,
          name: 'Logistics Emergency Protocol Agent',
          scenarioType: 'emergency_protocol',
          prompt: PROMPT_TEMPLATES.EMERGENCY_PROTOCOL,
          structuredFields: createMutableFields(SCENARIO_FIELDS.EMERGENCY_PROTOCOL)
        });
      } else {
        setConfig({
          ...config,
          name: 'Logistics Dispatch Agent',
          scenarioType: 'general',
          prompt: PROMPT_TEMPLATES.GENERAL_DISPATCHER,
          structuredFields: createMutableFields(SCENARIO_FIELDS.GENERAL)
        });
      }
    } catch (error) {
      showError(createError(
        'INITIALIZATION_ERROR',
        'Failed to load scenario template',
        'Unable to load the selected scenario. Please try again.',
        'medium'
      ));
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <ErrorDisplay
        error={errorState.error!}
        isVisible={errorState.isVisible}
        onClose={clearError}
      />

      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Truck className="h-8 w-8 text-primary-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Agent Configuration</h1>
            <p className="text-gray-600">Configure your AI voice agent for optimal performance</p>
          </div>
        </div>

        <div className="space-y-6">
          {/* Agent Name */}
          <TextField
            label={LABELS.AGENT_NAME}
            value={config.name}
            onChange={(e) => setConfig({ ...config, name: e.target.value })}
            placeholder={PLACEHOLDERS.AGENT_NAME}
            required
          />

          {/* Scenario Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              {LABELS.SCENARIO_TYPE}
            </label>
            <div className="space-y-3">
              <ScenarioCard
                title={SCENARIO_DESCRIPTIONS.DRIVER_CHECKIN.title}
                description={SCENARIO_DESCRIPTIONS.DRIVER_CHECKIN.description}
                icon={Truck}
                isSelected={config.scenarioType === 'driver_checkin'}
                onClick={() => loadScenarioTemplate('driver_checkin')}
                variant="success"
              />

              <ScenarioCard
                title={SCENARIO_DESCRIPTIONS.EMERGENCY_PROTOCOL.title}
                description={SCENARIO_DESCRIPTIONS.EMERGENCY_PROTOCOL.description}
                icon={AlertTriangle}
                isSelected={config.scenarioType === 'emergency_protocol'}
                onClick={() => loadScenarioTemplate('emergency_protocol')}
                variant="danger"
              />

              <ScenarioCard
                title={SCENARIO_DESCRIPTIONS.GENERAL.title}
                description={SCENARIO_DESCRIPTIONS.GENERAL.description}
                icon={Settings}
                isSelected={config.scenarioType === 'general'}
                onClick={() => loadScenarioTemplate('general')}
                variant="default"
              />
            </div>
          </div>

          {/* Agent Prompt */}
          <TextArea
            label={LABELS.AGENT_PROMPT}
            value={config.prompt}
            onChange={(e) => setConfig({ ...config, prompt: e.target.value })}
            rows={8}
            className="font-mono text-sm"
            required
          />

          {/* Emergency Phrases */}
          <TextArea
            label={LABELS.EMERGENCY_PHRASES}
            value={config.emergencyPhrases.join(', ')}
            onChange={(e) => setConfig({
              ...config,
              emergencyPhrases: e.target.value.split(',').map(phrase => phrase.trim()).filter(Boolean)
            })}
            rows={2}
            helpText={PLACEHOLDERS.SEPARATE_WITH_COMMAS}
            placeholder={PLACEHOLDERS.EMERGENCY_PHRASES}
          />
        </div>

        <div className="flex justify-end space-x-4 mt-8 pt-6 border-t">
          <Button
            onClick={handleSave}
            icon={Save}
            variant="primary"
          >
            {MESSAGES.ACTIONS.SAVE_CONFIGURATION}
          </Button>

          <Button
            onClick={onStartCall}
            icon={Play}
            variant="success"
          >
            {MESSAGES.ACTIONS.START_TEST_CALL}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default AgentConfiguration;