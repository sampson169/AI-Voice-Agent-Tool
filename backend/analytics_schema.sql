-- Analytics Database Schema Extension for PIPECAT Migration
-- Run this after the main database_setup.sql to add analytics capabilities

-- Create rtvi_events table for real-time voice interaction analytics
CREATE TABLE IF NOT EXISTS rtvi_events (
  event_id TEXT PRIMARY KEY,
  call_id TEXT NOT NULL REFERENCES call_results(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  data JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create call_metrics table for aggregated call analytics
CREATE TABLE IF NOT EXISTS call_metrics (
  call_id TEXT PRIMARY KEY REFERENCES call_results(id) ON DELETE CASCADE,
  start_time TIMESTAMP WITH TIME ZONE NOT NULL,
  end_time TIMESTAMP WITH TIME ZONE,
  duration_seconds DECIMAL(10,3),
  total_tokens INTEGER DEFAULT 0,
  interruption_count INTEGER DEFAULT 0,
  sentiment_shifts INTEGER DEFAULT 0,
  final_outcome TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create analytics_aggregations table for pre-computed analytics
CREATE TABLE IF NOT EXISTS analytics_aggregations (
  id SERIAL PRIMARY KEY,
  date_range_start DATE NOT NULL,
  date_range_end DATE NOT NULL,
  total_calls INTEGER DEFAULT 0,
  avg_call_duration DECIMAL(10,3) DEFAULT 0.0,
  total_interruptions INTEGER DEFAULT 0,
  emergency_calls INTEGER DEFAULT 0,
  successful_calls INTEGER DEFAULT 0,
  total_tokens_spent INTEGER DEFAULT 0,
  avg_tokens_per_call DECIMAL(10,3) DEFAULT 0.0,
  in_transit_updates INTEGER DEFAULT 0,
  arrival_confirmations INTEGER DEFAULT 0,
  emergency_escalations INTEGER DEFAULT 0,
  computed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(date_range_start, date_range_end)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_rtvi_events_call_id ON rtvi_events(call_id);
CREATE INDEX IF NOT EXISTS idx_rtvi_events_type ON rtvi_events(event_type);
CREATE INDEX IF NOT EXISTS idx_rtvi_events_timestamp ON rtvi_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_call_metrics_start_time ON call_metrics(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_call_metrics_outcome ON call_metrics(final_outcome);
CREATE INDEX IF NOT EXISTS idx_analytics_aggregations_date ON analytics_aggregations(date_range_start DESC, date_range_end DESC);

-- Add analytics-related columns to existing call_results table
ALTER TABLE call_results 
ADD COLUMN IF NOT EXISTS pipecat_call BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS analytics_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS end_time TIMESTAMP WITH TIME ZONE;

-- Create function to automatically compute daily aggregations
CREATE OR REPLACE FUNCTION compute_daily_analytics(target_date DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
DECLARE
    start_of_day TIMESTAMP WITH TIME ZONE;
    end_of_day TIMESTAMP WITH TIME ZONE;
    call_data RECORD;
BEGIN
    start_of_day := target_date::TIMESTAMP WITH TIME ZONE;
    end_of_day := (target_date + INTERVAL '1 day')::TIMESTAMP WITH TIME ZONE;
    
    -- Get aggregated data for the day
    SELECT 
        COUNT(*) as total_calls,
        COALESCE(AVG(duration_seconds), 0) as avg_duration,
        COALESCE(SUM(interruption_count), 0) as total_interruptions,
        COALESCE(SUM(CASE WHEN final_outcome = 'Emergency Escalation' THEN 1 ELSE 0 END), 0) as emergency_calls,
        COALESCE(SUM(CASE WHEN final_outcome IS NOT NULL THEN 1 ELSE 0 END), 0) as successful_calls,
        COALESCE(SUM(total_tokens), 0) as total_tokens,
        COALESCE(AVG(total_tokens), 0) as avg_tokens,
        COALESCE(SUM(CASE WHEN final_outcome = 'In-Transit Update' THEN 1 ELSE 0 END), 0) as in_transit,
        COALESCE(SUM(CASE WHEN final_outcome = 'Arrival Confirmation' THEN 1 ELSE 0 END), 0) as arrivals,
        COALESCE(SUM(CASE WHEN final_outcome = 'Emergency Escalation' THEN 1 ELSE 0 END), 0) as emergencies
    INTO call_data
    FROM call_metrics 
    WHERE start_time >= start_of_day AND start_time < end_of_day;
    
    -- Insert or update aggregation
    INSERT INTO analytics_aggregations (
        date_range_start, date_range_end, total_calls, avg_call_duration,
        total_interruptions, emergency_calls, successful_calls, total_tokens_spent,
        avg_tokens_per_call, in_transit_updates, arrival_confirmations, emergency_escalations
    ) VALUES (
        target_date, target_date, call_data.total_calls, call_data.avg_duration,
        call_data.total_interruptions, call_data.emergency_calls, call_data.successful_calls,
        call_data.total_tokens, call_data.avg_tokens, call_data.in_transit,
        call_data.arrivals, call_data.emergencies
    )
    ON CONFLICT (date_range_start, date_range_end) 
    DO UPDATE SET
        total_calls = EXCLUDED.total_calls,
        avg_call_duration = EXCLUDED.avg_call_duration,
        total_interruptions = EXCLUDED.total_interruptions,
        emergency_calls = EXCLUDED.emergency_calls,
        successful_calls = EXCLUDED.successful_calls,
        total_tokens_spent = EXCLUDED.total_tokens_spent,
        avg_tokens_per_call = EXCLUDED.avg_tokens_per_call,
        in_transit_updates = EXCLUDED.in_transit_updates,
        arrival_confirmations = EXCLUDED.arrival_confirmations,
        emergency_escalations = EXCLUDED.emergency_escalations,
        computed_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update call_metrics when call_results changes
CREATE OR REPLACE FUNCTION update_call_metrics_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Only update if this is a PIPECAT call
    IF NEW.pipecat_call = TRUE THEN
        INSERT INTO call_metrics (call_id, start_time, end_time)
        VALUES (NEW.id, NEW.start_time, NEW.end_time)
        ON CONFLICT (call_id) DO UPDATE SET
            end_time = EXCLUDED.end_time,
            updated_at = NOW();
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER call_results_to_metrics_trigger
    AFTER INSERT OR UPDATE ON call_results
    FOR EACH ROW
    EXECUTE FUNCTION update_call_metrics_trigger();

-- Create view for easy analytics querying
CREATE OR REPLACE VIEW analytics_summary AS
SELECT 
    cm.call_id,
    cr.call_request->>'driverName' as driver_name,
    cr.call_request->>'loadNumber' as load_number,
    cr.summary->>'call_outcome' as call_outcome,
    cm.start_time,
    cm.end_time,
    cm.duration_seconds,
    cm.total_tokens,
    cm.interruption_count,
    cm.sentiment_shifts,
    cm.final_outcome,
    (SELECT COUNT(*) FROM rtvi_events re WHERE re.call_id = cm.call_id) as total_events,
    (SELECT COUNT(*) FROM rtvi_events re WHERE re.call_id = cm.call_id AND re.event_type = 'emergency_keyword_detected') as emergency_events
FROM call_metrics cm
JOIN call_results cr ON cm.call_id = cr.id
WHERE cr.pipecat_call = TRUE
ORDER BY cm.start_time DESC;

-- Insert sample data for testing (optional)
INSERT INTO analytics_aggregations (
    date_range_start, date_range_end, total_calls, avg_call_duration,
    total_interruptions, emergency_calls, successful_calls, total_tokens_spent,
    avg_tokens_per_call, in_transit_updates, arrival_confirmations, emergency_escalations
) VALUES (
    CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE - INTERVAL '1 day',
    15, 45.5, 8, 2, 13, 2500, 166.7, 8, 3, 2
) ON CONFLICT (date_range_start, date_range_end) DO NOTHING;

-- Verify new tables were created
SELECT 'Analytics tables created successfully!' as status;
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('rtvi_events', 'call_metrics', 'analytics_aggregations')
ORDER BY table_name;