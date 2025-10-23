import React, { useState, useEffect } from 'react';
import { Phone, PhoneOff, Activity, Users, Clock, TrendingUp, AlertTriangle } from 'lucide-react';
import LoadingSpinner from '../ui/LoadingSpinner';
import config from '../../utils/config';

interface LiveCall {
  call_id: string;
  driver_name: string;
  phone_number: string;
  start_time: string;
  duration_seconds: number;
  current_phase: string;
  quality_score: number;
  sentiment: string;
  emergency_probability: number;
  completion_probability: number;
  interruption_count: number;
  conversation_turns: number;
}

interface LiveMetrics {
  active_calls: number;
  total_calls_today: number;
  avg_call_duration: number;
  emergency_calls_today: number;
  quality_score_avg: number;
}

const LiveCallMonitor: React.FC = () => {
  const [activeCalls, setActiveCalls] = useState<LiveCall[]>([]);
  const [liveMetrics, setLiveMetrics] = useState<LiveMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchLiveData = async () => {
    try {
      setError(null);

      const callsResponse = await fetch(`${config.apiBaseUrl}/api/analytics/live/calls`);
      if (callsResponse.ok) {
        const callsData = await callsResponse.json();
        setActiveCalls(callsData.active_calls || []);
      }

      const metricsResponse = await fetch(`${config.apiBaseUrl}/api/analytics/live/metrics`);
      if (metricsResponse.ok) {
        const metricsData = await metricsResponse.json();
        setLiveMetrics(metricsData.metrics);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch live data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLiveData();

    let interval: number;
    if (autoRefresh) {
      interval = setInterval(fetchLiveData, 5000); 
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getQualityColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSentimentColor = (sentiment: string): string => {
    switch (sentiment) {
      case 'positive': return 'text-green-600';
      case 'negative': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getPhaseColor = (phase: string): string => {
    switch (phase) {
      case 'greeting': return 'bg-blue-100 text-blue-800';
      case 'information_gathering': return 'bg-yellow-100 text-yellow-800';
      case 'problem_solving': return 'bg-orange-100 text-orange-800';
      case 'conclusion': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner />
        <span className="ml-3 text-gray-600">Loading live call data...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <Activity className="h-8 w-8 text-red-500 mr-3 animate-pulse" />
            Live Call Monitor
          </h2>
          <p className="text-gray-600 mt-1">Real-time monitoring of active voice calls</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm text-gray-600">Auto-refresh</span>
          </label>
          
          <button
            onClick={fetchLiveData}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:ring-2 focus:ring-primary-500"
          >
            Refresh Now
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <AlertTriangle className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {liveMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center">
              <Phone className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Calls</p>
                <p className="text-2xl font-bold text-gray-900">{liveMetrics.active_calls}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Calls Today</p>
                <p className="text-2xl font-bold text-gray-900">{liveMetrics.total_calls_today}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Duration</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatDuration(Math.round(liveMetrics.avg_call_duration))}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Emergencies</p>
                <p className="text-2xl font-bold text-gray-900">{liveMetrics.emergency_calls_today}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Quality Score</p>
                <p className={`text-2xl font-bold ${getQualityColor(liveMetrics.quality_score_avg)}`}>
                  {(liveMetrics.quality_score_avg * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Active Calls</h3>
          <p className="text-sm text-gray-600">Real-time status of ongoing voice calls</p>
        </div>

        {activeCalls.length === 0 ? (
          <div className="p-8 text-center">
            <PhoneOff className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Active Calls</h3>
            <p className="text-gray-600">There are currently no active voice calls.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Driver
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Phase
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quality
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sentiment
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Emergency Risk
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {activeCalls.map((call) => (
                  <tr key={call.call_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{call.driver_name}</div>
                        <div className="text-sm text-gray-500">{call.phone_number}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{formatDuration(call.duration_seconds)}</div>
                      <div className="text-xs text-gray-500">{call.conversation_turns} turns</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPhaseColor(call.current_phase)}`}>
                        {call.current_phase.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className={`h-2 rounded-full ${getQualityColor(call.quality_score).replace('text-', 'bg-')}`}
                            style={{ width: `${call.quality_score * 100}%` }}
                          ></div>
                        </div>
                        <span className={`text-sm font-medium ${getQualityColor(call.quality_score)}`}>
                          {(call.quality_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${getSentimentColor(call.sentiment)}`}>
                        {call.sentiment}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {call.emergency_probability > 0.7 ? (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                            HIGH ({(call.emergency_probability * 100).toFixed(0)}%)
                          </span>
                        ) : call.emergency_probability > 0.3 ? (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
                            MEDIUM ({(call.emergency_probability * 100).toFixed(0)}%)
                          </span>
                        ) : (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                            LOW ({(call.emergency_probability * 100).toFixed(0)}%)
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="h-2 bg-blue-600 rounded-full"
                            style={{ width: `${call.completion_probability * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900">
                          {(call.completion_probability * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => window.open(`/calls/${call.call_id}/live`, '_blank')}
                        className="text-primary-600 hover:text-primary-900 mr-3"
                      >
                        Monitor
                      </button>
                      {call.emergency_probability > 0.7 && (
                        <button
                          onClick={() => alert('Emergency escalation would be triggered')}
                          className="text-red-600 hover:text-red-900"
                        >
                          Escalate
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveCallMonitor;