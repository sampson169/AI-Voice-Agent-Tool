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

CREATE INDEX IF NOT EXISTS idx_rtvi_events_call_id ON rtvi_events(call_id);
CREATE INDEX IF NOT EXISTS idx_rtvi_events_type ON rtvi_events(event_type);
CREATE INDEX IF NOT EXISTS idx_rtvi_events_timestamp ON rtvi_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_call_metrics_start_time ON call_metrics(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_call_metrics_outcome ON call_metrics(final_outcome);
CREATE INDEX IF NOT EXISTS idx_analytics_aggregations_date ON analytics_aggregations(date_range_start DESC, date_range_end DESC);

ALTER TABLE call_results 
ADD COLUMN IF NOT EXISTS pipecat_call BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS analytics_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS end_time TIMESTAMP WITH TIME ZONE;

CREATE OR REPLACE FUNCTION compute_daily_analytics(target_date DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
DECLARE
    start_of_day TIMESTAMP WITH TIME ZONE;
    end_of_day TIMESTAMP WITH TIME ZONE;
    call_data RECORD;
BEGIN
    start_of_day := target_date::TIMESTAMP WITH TIME ZONE;
    end_of_day := (target_date + INTERVAL '1 day')::TIMESTAMP WITH TIME ZONE;
    
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

CREATE OR REPLACE FUNCTION update_call_metrics_trigger()
RETURNS TRIGGER AS $$
BEGIN
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

INSERT INTO analytics_aggregations (
    date_range_start, date_range_end, total_calls, avg_call_duration,
    total_interruptions, emergency_calls, successful_calls, total_tokens_spent,
    avg_tokens_per_call, in_transit_updates, arrival_confirmations, emergency_escalations
) VALUES (
    CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE - INTERVAL '1 day',
    15, 45.5, 8, 2, 13, 2500, 166.7, 8, 3, 2
) ON CONFLICT (date_range_start, date_range_end) DO NOTHING;

SELECT 'Analytics tables created successfully!' as status;
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('rtvi_events', 'call_metrics', 'analytics_aggregations')
ORDER BY table_name;

CREATE TABLE IF NOT EXISTS system_events (
  event_id TEXT PRIMARY KEY,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  event_type TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'error', 'critical')),
  component TEXT NOT NULL CHECK (component IN ('pipecat_engine', 'llm_service', 'database', 'audio_processing', 'error_tracking', 'voice_quality', 'system')),
  message TEXT NOT NULL,
  call_id TEXT REFERENCES call_results(id) ON DELETE SET NULL,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS system_alerts (
  alert_id TEXT PRIMARY KEY,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'error', 'critical')),
  component TEXT NOT NULL CHECK (component IN ('pipecat_engine', 'llm_service', 'database', 'audio_processing', 'error_tracking', 'voice_quality', 'system')),
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  call_id TEXT REFERENCES call_results(id) ON DELETE SET NULL,
  acknowledged BOOLEAN DEFAULT FALSE,
  resolved BOOLEAN DEFAULT FALSE,
  resolution_note TEXT,
  resolved_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS system_health_metrics (
  metric_id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  component TEXT NOT NULL,
  metric_name TEXT NOT NULL,
  metric_value DECIMAL(15,6) NOT NULL,
  unit TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS voice_quality_assessments (
  assessment_id TEXT PRIMARY KEY,
  call_id TEXT NOT NULL REFERENCES call_results(id) ON DELETE CASCADE,
  overall_score DECIMAL(3,2) CHECK (overall_score >= 0 AND overall_score <= 1),
  audio_quality_score DECIMAL(3,2) CHECK (audio_quality_score >= 0 AND audio_quality_score <= 1),
  speech_clarity_score DECIMAL(3,2) CHECK (speech_clarity_score >= 0 AND speech_clarity_score <= 1),
  conversation_flow_score DECIMAL(3,2) CHECK (conversation_flow_score >= 0 AND conversation_flow_score <= 1),
  response_time_score DECIMAL(3,2) CHECK (response_time_score >= 0 AND response_time_score <= 1),
  naturalness_score DECIMAL(3,2) CHECK (naturalness_score >= 0 AND naturalness_score <= 1),
  assessment_data JSONB DEFAULT '{}',
  issues_detected TEXT[],
  recommendations TEXT[],
  assessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS performance_metrics (
  metric_id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  metric_category TEXT NOT NULL,
  response_time_avg DECIMAL(10,3),
  throughput_per_hour INTEGER,
  error_rate DECIMAL(5,4),
  cpu_usage_avg DECIMAL(5,2),
  memory_usage_avg DECIMAL(5,2),
  disk_usage_avg DECIMAL(5,2),
  network_latency_avg DECIMAL(10,3),
  active_connections INTEGER,
  queue_depth INTEGER,
  cache_hit_rate DECIMAL(5,4),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_system_events_timestamp ON system_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_system_events_severity ON system_events(severity);
CREATE INDEX IF NOT EXISTS idx_system_events_component ON system_events(component);
CREATE INDEX IF NOT EXISTS idx_system_events_call_id ON system_events(call_id);

CREATE INDEX IF NOT EXISTS idx_system_alerts_timestamp ON system_alerts(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_system_alerts_severity ON system_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_system_alerts_resolved ON system_alerts(resolved);
CREATE INDEX IF NOT EXISTS idx_system_alerts_acknowledged ON system_alerts(acknowledged);

CREATE INDEX IF NOT EXISTS idx_system_health_metrics_timestamp ON system_health_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_system_health_metrics_component ON system_health_metrics(component);
CREATE INDEX IF NOT EXISTS idx_system_health_metrics_name ON system_health_metrics(metric_name);

CREATE INDEX IF NOT EXISTS idx_voice_quality_assessments_call_id ON voice_quality_assessments(call_id);
CREATE INDEX IF NOT EXISTS idx_voice_quality_assessments_score ON voice_quality_assessments(overall_score);
CREATE INDEX IF NOT EXISTS idx_voice_quality_assessments_assessed_at ON voice_quality_assessments(assessed_at DESC);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_category ON performance_metrics(metric_category);

CREATE OR REPLACE VIEW recent_system_events AS
SELECT 
    event_id,
    timestamp,
    event_type,
    severity,
    component,
    message,
    call_id,
    metadata
FROM system_events
WHERE timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

CREATE OR REPLACE VIEW active_alerts AS
SELECT 
    alert_id,
    timestamp,
    severity,
    component,
    title,
    description,
    call_id,
    acknowledged,
    created_at
FROM system_alerts
WHERE resolved = FALSE
ORDER BY 
    CASE severity 
        WHEN 'critical' THEN 1
        WHEN 'error' THEN 2 
        WHEN 'warning' THEN 3
        WHEN 'info' THEN 4
    END,
    timestamp DESC;

CREATE OR REPLACE VIEW system_health_summary AS
SELECT 
    component,
    COUNT(*) as metric_count,
    AVG(metric_value) as avg_value,
    MIN(metric_value) as min_value,
    MAX(metric_value) as max_value,
    MAX(timestamp) as last_updated
FROM system_health_metrics
WHERE timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY component
ORDER BY component;

CREATE OR REPLACE VIEW call_quality_trends AS
SELECT 
    DATE(assessed_at) as assessment_date,
    COUNT(*) as total_assessments,
    AVG(overall_score) as avg_overall_score,
    AVG(audio_quality_score) as avg_audio_quality,
    AVG(speech_clarity_score) as avg_speech_clarity,
    AVG(conversation_flow_score) as avg_conversation_flow,
    AVG(response_time_score) as avg_response_time,
    AVG(naturalness_score) as avg_naturalness,
    COUNT(CASE WHEN overall_score < 0.6 THEN 1 END) as low_quality_calls
FROM voice_quality_assessments
WHERE assessed_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(assessed_at)
ORDER BY assessment_date DESC;

CREATE OR REPLACE FUNCTION cleanup_monitoring_data(retention_days INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_events INTEGER;
    deleted_metrics INTEGER;
    deleted_assessments INTEGER;
    cutoff_date TIMESTAMP WITH TIME ZONE;
BEGIN
    cutoff_date := NOW() - (retention_days || ' days')::INTERVAL;
    
    DELETE FROM system_events WHERE timestamp < cutoff_date;
    GET DIAGNOSTICS deleted_events = ROW_COUNT;
    
    DELETE FROM system_health_metrics WHERE timestamp < cutoff_date;
    GET DIAGNOSTICS deleted_metrics = ROW_COUNT;
    
    DELETE FROM voice_quality_assessments WHERE assessed_at < cutoff_date;
    GET DIAGNOSTICS deleted_assessments = ROW_COUNT;
    
    DELETE FROM performance_metrics WHERE timestamp < NOW() - INTERVAL '90 days';
    
    RETURN deleted_events + deleted_metrics + deleted_assessments;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION aggregate_performance_metrics(target_date DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
DECLARE
    start_of_day TIMESTAMP WITH TIME ZONE;
    end_of_day TIMESTAMP WITH TIME ZONE;
BEGIN
    start_of_day := target_date::TIMESTAMP WITH TIME ZONE;
    end_of_day := (target_date + INTERVAL '1 day')::TIMESTAMP WITH TIME ZONE;
    
    INSERT INTO performance_metrics (
        timestamp, metric_category, response_time_avg, throughput_per_hour,
        error_rate, cpu_usage_avg, memory_usage_avg, disk_usage_avg,
        network_latency_avg, cache_hit_rate, metadata
    )
    SELECT 
        start_of_day,
        'daily_aggregate',
        AVG(response_time_avg),
        SUM(throughput_per_hour),
        AVG(error_rate),
        AVG(cpu_usage_avg),
        AVG(memory_usage_avg),
        AVG(disk_usage_avg),
        AVG(network_latency_avg),
        AVG(cache_hit_rate),
        jsonb_build_object(
            'source', 'daily_aggregation',
            'aggregated_from', COUNT(*),
            'date', target_date
        )
    FROM performance_metrics
    WHERE timestamp >= start_of_day 
    AND timestamp < end_of_day
    AND metric_category != 'daily_aggregate'
    HAVING COUNT(*) > 0;
END;
$$ LANGUAGE plpgsql;

INSERT INTO system_events (event_id, event_type, severity, component, message, metadata) VALUES
('evt_' || generate_random_uuid(), 'system_startup', 'info', 'system', 'System monitoring initialized', '{"version": "1.0.0"}'),
('evt_' || generate_random_uuid(), 'call_processed', 'info', 'pipecat_engine', 'Call processed successfully', '{"duration": 45.2}'),
('evt_' || generate_random_uuid(), 'high_memory_usage', 'warning', 'system', 'Memory usage above 80%', '{"usage_percent": 85.3}');

INSERT INTO system_health_metrics (component, metric_name, metric_value, unit) VALUES
('pipecat_engine', 'cpu_usage', 35.2, 'percent'),
('pipecat_engine', 'memory_usage', 68.5, 'percent'),
('llm_service', 'response_time', 2.1, 'seconds'),
('database', 'connection_count', 12, 'connections'),
('audio_processing', 'processing_latency', 0.8, 'seconds');

SELECT 'System monitoring tables created successfully!' as status;
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('system_events', 'system_alerts', 'system_health_metrics', 'voice_quality_assessments', 'performance_metrics')
ORDER BY table_name;