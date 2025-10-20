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

-- Create call_metrics table for PIPECAT analytics
CREATE TABLE IF NOT EXISTS call_metrics (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  call_id TEXT NOT NULL,
  start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  end_time TIMESTAMP WITH TIME ZONE,
  duration_seconds INTEGER DEFAULT 0,
  total_tokens INTEGER DEFAULT 0,
  interruption_count INTEGER DEFAULT 0,
  outcome TEXT,
  emergency_detected BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create rtvi_events table for detailed analytics
CREATE TABLE IF NOT EXISTS rtvi_events (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  call_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  event_data JSONB DEFAULT '{}',
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create daily_analytics table for aggregated data
CREATE TABLE IF NOT EXISTS daily_analytics (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  date_range_start DATE NOT NULL,
  date_range_end DATE NOT NULL,
  total_calls INTEGER DEFAULT 0,
  avg_call_duration DECIMAL(10,2) DEFAULT 0,
  total_interruptions INTEGER DEFAULT 0,
  emergency_calls INTEGER DEFAULT 0,
  total_tokens_spent INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(date_range_start, date_range_end)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_agent_configs_name ON agent_configs(name);
CREATE INDEX IF NOT EXISTS idx_call_results_timestamp ON call_results(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_call_results_retell_id ON call_results(retell_call_id);
CREATE INDEX IF NOT EXISTS idx_call_metrics_call_id ON call_metrics(call_id);
CREATE INDEX IF NOT EXISTS idx_call_metrics_start_time ON call_metrics(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_rtvi_events_call_id ON rtvi_events(call_id);
CREATE INDEX IF NOT EXISTS idx_rtvi_events_type ON rtvi_events(event_type);
CREATE INDEX IF NOT EXISTS idx_rtvi_events_timestamp ON rtvi_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_daily_analytics_date ON daily_analytics(date_range_start DESC);

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

-- Insert some sample data for testing analytics
INSERT INTO call_metrics (call_id, start_time, end_time, duration_seconds, total_tokens, interruption_count, outcome, emergency_detected) 
SELECT 'test-call-1', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '3 minutes', 180, 1200, 2, 'In-Transit Update', FALSE
WHERE NOT EXISTS (SELECT 1 FROM call_metrics WHERE call_id = 'test-call-1');

INSERT INTO call_metrics (call_id, start_time, end_time, duration_seconds, total_tokens, interruption_count, outcome, emergency_detected) 
SELECT 'test-call-2', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days' + INTERVAL '5 minutes', 300, 1800, 1, 'Arrival Confirmation', FALSE
WHERE NOT EXISTS (SELECT 1 FROM call_metrics WHERE call_id = 'test-call-2');

INSERT INTO call_metrics (call_id, start_time, end_time, duration_seconds, total_tokens, interruption_count, outcome, emergency_detected) 
SELECT 'test-call-3', NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '8 minutes', 480, 2400, 5, 'Emergency Escalation', TRUE
WHERE NOT EXISTS (SELECT 1 FROM call_metrics WHERE call_id = 'test-call-3');

-- Insert sample RTVI events
INSERT INTO rtvi_events (call_id, event_type, event_data) 
SELECT 'test-call-1', 'call_started', '{"timestamp": "2025-10-19T10:00:00Z"}'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM rtvi_events WHERE call_id = 'test-call-1' AND event_type = 'call_started');

INSERT INTO rtvi_events (call_id, event_type, event_data) 
SELECT 'test-call-1', 'user_speech', '{"text": "I am on I-10, about 50 miles out"}'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM rtvi_events WHERE call_id = 'test-call-1' AND event_type = 'user_speech');

INSERT INTO rtvi_events (call_id, event_type, event_data) 
SELECT 'test-call-1', 'bot_speech', '{"text": "Great! What is your current location?"}'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM rtvi_events WHERE call_id = 'test-call-1' AND event_type = 'bot_speech');

INSERT INTO rtvi_events (call_id, event_type, event_data) 
SELECT 'test-call-1', 'call_ended', '{"timestamp": "2025-10-19T10:03:00Z"}'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM rtvi_events WHERE call_id = 'test-call-1' AND event_type = 'call_ended');

INSERT INTO rtvi_events (call_id, event_type, event_data) 
SELECT 'test-call-2', 'call_started', '{"timestamp": "2025-10-18T14:00:00Z"}'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM rtvi_events WHERE call_id = 'test-call-2' AND event_type = 'call_started');

INSERT INTO rtvi_events (call_id, event_type, event_data) 
SELECT 'test-call-2', 'user_speech', '{"text": "I have arrived at the delivery location"}'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM rtvi_events WHERE call_id = 'test-call-2' AND event_type = 'user_speech');

INSERT INTO rtvi_events (call_id, event_type, event_data) 
SELECT 'test-call-2', 'bot_speech', '{"text": "Perfect! Please confirm your POD"}'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM rtvi_events WHERE call_id = 'test-call-2' AND event_type = 'bot_speech');

INSERT INTO rtvi_events (call_id, event_type, event_data) 
SELECT 'test-call-2', 'call_ended', '{"timestamp": "2025-10-18T14:05:00Z"}'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM rtvi_events WHERE call_id = 'test-call-2' AND event_type = 'call_ended');

-- Insert sample daily analytics data
INSERT INTO daily_analytics (date_range_start, date_range_end, total_calls, avg_call_duration, total_interruptions, emergency_calls, total_tokens_spent)
SELECT '2025-10-17'::date, '2025-10-17'::date, 1, 480.00, 5, 1, 2400
WHERE NOT EXISTS (SELECT 1 FROM daily_analytics WHERE date_range_start = '2025-10-17');

INSERT INTO daily_analytics (date_range_start, date_range_end, total_calls, avg_call_duration, total_interruptions, emergency_calls, total_tokens_spent)
SELECT '2025-10-18'::date, '2025-10-18'::date, 1, 300.00, 1, 0, 1800  
WHERE NOT EXISTS (SELECT 1 FROM daily_analytics WHERE date_range_start = '2025-10-18');

INSERT INTO daily_analytics (date_range_start, date_range_end, total_calls, avg_call_duration, total_interruptions, emergency_calls, total_tokens_spent)
SELECT '2025-10-19'::date, '2025-10-19'::date, 1, 180.00, 2, 0, 1200
WHERE NOT EXISTS (SELECT 1 FROM daily_analytics WHERE date_range_start = '2025-10-19');

-- Verify tables were created
SELECT 'Tables created successfully!' as status;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name IN ('agent_configs', 'call_results', 'call_metrics', 'rtvi_events', 'daily_analytics');