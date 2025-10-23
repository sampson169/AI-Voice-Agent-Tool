import React, { useState, useEffect } from 'react';
import Card from './ui/Card';
import StatusBadge from './ui/StatusBadge';
import LoadingSpinner from './ui/LoadingSpinner';

interface SystemHealth {
  overall_status: string;
  component_status: Record<string, string>;
  performance_metrics: Record<string, number>;
  last_check: string;
}

interface ErrorSummary {
  total_errors_24h: number;
  critical_errors: number;
  error_rate: number;
  top_error_type: string;
}

interface AlertInfo {
  active_alerts: number;
  critical_alerts: number;
  warning_alerts: number;
}

interface PerformanceMetrics {
  average_response_time: number;
  system_load: number;
  memory_usage: number;
  disk_usage: number;
  network_latency: number;
}

interface QualityMetrics {
  current_quality_score: number;
  quality_trend_24h: string;
  calls_processed_24h: number;
  successful_calls_percentage: number;
}

interface UptimeInfo {
  current_uptime_hours: number;
  uptime_percentage_30d: number;
  last_incident: string;
}

interface DashboardData {
  system_health: SystemHealth;
  error_summary: ErrorSummary;
  alerts: AlertInfo;
  performance: PerformanceMetrics;
  quality_metrics: QualityMetrics;
  uptime: UptimeInfo;
  last_updated: string;
}

interface SystemAlert {
  alert_id: string;
  timestamp: string;
  severity: string;
  component: string;
  title: string;
  description: string;
  call_id?: string;
  acknowledged: boolean;
}

export const SystemMonitoringDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [activeAlerts, setActiveAlerts] = useState<SystemAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedView, setSelectedView] = useState<'overview' | 'alerts' | 'performance' | 'errors'>('overview');

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [dashboardResponse, alertsResponse] = await Promise.all([
        fetch('/api/analytics/monitoring/dashboard'),
        fetch('/api/analytics/system/alerts')
      ]);

      if (!dashboardResponse.ok || !alertsResponse.ok) {
        throw new Error('Failed to fetch monitoring data');
      }

      const dashboardResult = await dashboardResponse.json();
      const alertsResult = await alertsResponse.json();

      setDashboardData(dashboardResult.dashboard);
      setActiveAlerts(alertsResult.alerts || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch monitoring data');
    } finally {
      setLoading(false);
    }
  };

  const resolveAlert = async (alertId: string) => {
    try {
      const response = await fetch(`/api/analytics/system/alerts/${alertId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resolution_note: 'Resolved from dashboard' })
      });

      if (response.ok) {
        setActiveAlerts(prev => prev.filter(alert => alert.alert_id !== alertId));
      }
    } catch (err) {
      console.error('Failed to resolve alert:', err);
    }
  };

  const getStatusVariant = (status: string): 'success' | 'warning' | 'danger' | 'info' | 'neutral' => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'good':
      case 'stable':
        return 'success';
      case 'warning':
      case 'degraded':
        return 'warning';
      case 'critical':
      case 'error':
        return 'danger';
      default:
        return 'neutral';
    }
  };

  const getSeverityVariant = (severity: string): 'success' | 'warning' | 'danger' | 'info' | 'neutral' => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'danger';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'neutral';
    }
  };

  const formatUptime = (hours: number) => {
    const days = Math.floor(hours / 24);
    const remainingHours = Math.floor(hours % 24);
    return `${days}d ${remainingHours}h`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-red-800 mb-2">Error</h3>
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-yellow-800 mb-2">No Data</h3>
          <p className="text-yellow-700">No monitoring data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">System Monitoring</h1>
          <p className="text-gray-600">
            Last updated: {new Date(dashboardData.last_updated).toLocaleString()}
          </p>
        </div>
        
        <div className="flex space-x-2">
          {['overview', 'alerts', 'performance', 'errors'].map((view) => (
            <button
              key={view}
              onClick={() => setSelectedView(view as any)}
              className={`px-4 py-2 rounded-lg capitalize ${
                selectedView === view
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {view}
            </button>
          ))}
        </div>
      </div>

      {/* Overview Cards */}
      {selectedView === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* System Health */}
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">System Health</p>
                <StatusBadge variant={getStatusVariant(dashboardData.system_health.overall_status)}>
                  {dashboardData.system_health.overall_status}
                </StatusBadge>
              </div>
              <div className="text-3xl">🏥</div>
            </div>
          </Card>

          {/* Active Alerts */}
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Alerts</p>
                <p className="text-2xl font-bold">
                  {dashboardData.alerts.active_alerts}
                </p>
                <p className="text-xs text-red-600">
                  {dashboardData.alerts.critical_alerts} critical
                </p>
              </div>
              <div className="text-3xl">🚨</div>
            </div>
          </Card>

          {/* Performance */}
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Response Time</p>
                <p className="text-2xl font-bold">
                  {dashboardData.performance.average_response_time.toFixed(1)}s
                </p>
                <p className="text-xs text-gray-500">
                  Load: {(dashboardData.performance.system_load * 100).toFixed(0)}%
                </p>
              </div>
              <div className="text-3xl">⚡</div>
            </div>
          </Card>

          {/* Quality Score */}
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Call Quality</p>
                <p className="text-2xl font-bold">
                  {(dashboardData.quality_metrics.current_quality_score * 100).toFixed(0)}%
                </p>
                <p className="text-xs text-gray-500">
                  {dashboardData.quality_metrics.calls_processed_24h} calls today
                </p>
              </div>
              <div className="text-3xl">📞</div>
            </div>
          </Card>
        </div>
      )}

      {/* Detailed Views */}
      {selectedView === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* System Components */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Component Status</h3>
            <div className="space-y-3">
              {Object.entries(dashboardData.system_health.component_status || {}).map(([component, status]) => (
                <div key={component} className="flex justify-between items-center">
                  <span className="text-sm font-medium capitalize">{component}</span>
                  <StatusBadge variant={getStatusVariant(status)}>
                    {status}
                  </StatusBadge>
                </div>
              ))}
            </div>
          </Card>

          {/* Performance Metrics */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Performance Metrics</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Memory Usage</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${dashboardData.performance.memory_usage * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-600">
                    {(dashboardData.performance.memory_usage * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm">Disk Usage</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${dashboardData.performance.disk_usage * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-600">
                    {(dashboardData.performance.disk_usage * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm">Network Latency</span>
                <span className="text-sm font-medium">
                  {dashboardData.performance.network_latency.toFixed(1)}ms
                </span>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Alerts View */}
      {selectedView === 'alerts' && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Active Alerts</h3>
          {activeAlerts.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No active alerts</p>
          ) : (
            <div className="space-y-4">
              {activeAlerts.map((alert) => (
                <div 
                  key={alert.alert_id}
                  className="border rounded-lg p-4 flex justify-between items-start"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <StatusBadge variant={getSeverityVariant(alert.severity)}>
                        {alert.severity}
                      </StatusBadge>
                      <span className="text-sm text-gray-600">{alert.component}</span>
                      <span className="text-sm text-gray-500">
                        {new Date(alert.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <h4 className="font-medium text-gray-900">{alert.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{alert.description}</p>
                    {alert.call_id && (
                      <p className="text-xs text-gray-500 mt-2">Call ID: {alert.call_id}</p>
                    )}
                  </div>
                  <button
                    onClick={() => resolveAlert(alert.alert_id)}
                    className="ml-4 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Resolve
                  </button>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}

      {/* Performance View */}
      {selectedView === 'performance' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">System Resources</h3>
            <div className="space-y-4">
              {Object.entries(dashboardData.performance).map(([metric, value]) => (
                <div key={metric} className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium capitalize">
                      {metric.replace(/_/g, ' ')}
                    </span>
                    <span className="text-sm text-gray-600">
                      {typeof value === 'number' ? 
                        (metric.includes('usage') || metric.includes('load') ? 
                          `${(value * 100).toFixed(0)}%` : 
                          `${value.toFixed(2)}${metric.includes('time') ? 's' : metric.includes('latency') ? 'ms' : ''}`
                        ) : 
                        value
                      }
                    </span>
                  </div>
                  {typeof value === 'number' && (metric.includes('usage') || metric.includes('load')) && (
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          value > 0.8 ? 'bg-red-600' : value > 0.6 ? 'bg-yellow-600' : 'bg-green-600'
                        }`}
                        style={{ width: `${value * 100}%` }}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Uptime Information</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Current Uptime</p>
                <p className="text-2xl font-bold">
                  {formatUptime(dashboardData.uptime.current_uptime_hours)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">30-Day Availability</p>
                <p className="text-2xl font-bold text-green-600">
                  {dashboardData.uptime.uptime_percentage_30d.toFixed(2)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Last Incident</p>
                <p className="text-sm">
                  {new Date(dashboardData.uptime.last_incident).toLocaleString()}
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Errors View */}
      {selectedView === 'errors' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Error Summary (24h)</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Total Errors</p>
                <p className="text-3xl font-bold text-red-600">
                  {dashboardData.error_summary.total_errors_24h}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Critical Errors</p>
                <p className="text-2xl font-bold text-red-800">
                  {dashboardData.error_summary.critical_errors}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Error Rate</p>
                <p className="text-xl font-bold">
                  {dashboardData.error_summary.error_rate.toFixed(2)}/hour
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Top Error Type</p>
                <p className="text-sm font-medium text-gray-900">
                  {dashboardData.error_summary.top_error_type}
                </p>
              </div>
            </div>
          </Card>

          <Card className="lg:col-span-2 p-6">
            <h3 className="text-lg font-semibold mb-4">Quality Metrics</h3>
            <div className="grid grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-600">Current Quality Score</p>
                <p className="text-3xl font-bold text-green-600">
                  {(dashboardData.quality_metrics.current_quality_score * 100).toFixed(0)}%
                </p>
                <p className="text-sm text-gray-500">
                  Trend: {dashboardData.quality_metrics.quality_trend_24h}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Success Rate</p>
                <p className="text-3xl font-bold text-blue-600">
                  {dashboardData.quality_metrics.successful_calls_percentage.toFixed(1)}%
                </p>
                <p className="text-sm text-gray-500">
                  {dashboardData.quality_metrics.calls_processed_24h} calls processed
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};