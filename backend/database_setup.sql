-- Voice Agent Tool Database Schema
-- Run this in your Supabase SQL Editor to create the required tables

-- Create agent_configs table
CREATE TABLE IF NOT EXISTS agent_configs (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  prompt TEXT NOT NULL,
  scenario_type TEXT DEFAULT 'general',
  voice_settings JSONB DEFAULT '{}',
  emergency_phrases TEXT[] DEFAULT '{}',
  structured_fields JSONB DEFAULT '[]',
  retell_agent_id TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create call_results table  
CREATE TABLE IF NOT EXISTS call_results (
  id TEXT PRIMARY KEY,
  retell_call_id TEXT,
  call_request JSONB NOT NULL,
  transcript TEXT DEFAULT '',
  summary JSONB DEFAULT '{}',
  conversation_state JSONB DEFAULT '{}',
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  duration INTEGER DEFAULT 0
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_agent_configs_name ON agent_configs(name);
CREATE INDEX IF NOT EXISTS idx_call_results_timestamp ON call_results(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_call_results_retell_id ON call_results(retell_call_id);

-- Insert a default agent configuration for testing
INSERT INTO agent_configs (
  id, 
  name, 
  prompt, 
  scenario_type,
  voice_settings, 
  emergency_phrases, 
  structured_fields
) VALUES (
  'default-logistics-agent',
  'General Logistics Dispatcher',
  'You are a professional logistics dispatcher calling truck drivers for status updates. You handle both routine check-ins and emergency situations with equal professionalism. For normal calls, ask about status, location, and ETA. For emergencies, immediately ask about safety, location, and what happened, then escalate to human dispatcher.',
  'general',
  '{"voice_id": "11labs-Adrian", "speed": 1.0, "temperature": 0.7, "backchanneling": true, "filler_words": true, "interruption_sensitivity": "medium"}',
  '{"emergency", "accident", "breakdown", "medical", "help", "urgent", "blowout", "crash", "collision", "injury", "hurt", "stuck", "disabled"}',
  '[
    {"key": "call_outcome", "label": "Call Outcome", "type": "select", "options": ["In-Transit Update", "Arrival Confirmation", "Emergency Escalation"]},
    {"key": "driver_status", "label": "Driver Status", "type": "select", "options": ["Driving", "Delayed", "Arrived", "Unloading"]},
    {"key": "current_location", "label": "Current Location", "type": "text"},
    {"key": "eta", "label": "ETA", "type": "text"},
    {"key": "delay_reason", "label": "Delay Reason", "type": "select", "options": ["Heavy Traffic", "Weather", "Mechanical", "Loading/Unloading", "Fuel", "DOT/Legal", "Other", "None"]},
    {"key": "unloading_status", "label": "Unloading Status", "type": "select", "options": ["In Door", "Waiting for Lumper", "Detention", "N/A"]},
    {"key": "pod_reminder_acknowledged", "label": "POD Reminder", "type": "boolean"},
    {"key": "emergency_type", "label": "Emergency Type", "type": "select", "options": ["Accident", "Breakdown", "Medical", "Other"]},
    {"key": "safety_status", "label": "Safety Status", "type": "text"},
    {"key": "injury_status", "label": "Injury Status", "type": "text"},
    {"key": "emergency_location", "label": "Emergency Location", "type": "text"},
    {"key": "load_secure", "label": "Load Secure", "type": "boolean"},
    {"key": "escalation_status", "label": "Escalation Status", "type": "text"}
  ]'
) ON CONFLICT (id) DO UPDATE SET
  scenario_type = 'general',
  updated_at = NOW();

-- Verify tables were created
SELECT 'Tables created successfully!' as status;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name IN ('agent_configs', 'call_results');