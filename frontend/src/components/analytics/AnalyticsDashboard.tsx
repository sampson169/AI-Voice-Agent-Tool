import React, { useState, useEffect } from 'react';
import { RefreshCw, TrendingUp, Calendar } from 'lucide-react';
import AnalyticsMetrics from './AnalyticsMetrics';
import CallOutcomeChart from './CallOutcomeChart';
import AnalyticsTrendsChart from './AnalyticsTrendsChart';
import LoadingSpinner from '../ui/LoadingSpinner';
import config from '../../utils/config';

interface DashboardMetrics {
  total_calls: number;
  avg_call_duration: number;
  total_interruptions: number;
  total_tokens: number;
  avg_tokens_per_call: number;
  emergency_calls: number;
  successful_calls: number;
  outcomes: Record<string, number>;
  event_types: Record<string, number>;
}

interface OutcomeDistribution {
  outcome: string;
  count: number;
  percentage: number;
}

interface TrendData {
  date: string;
  total_calls: number;
  avg_duration: number;
  interruptions: number;
  emergency_calls: number;
  tokens_used: number;
}

const AnalyticsDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [outcomes, setOutcomes] = useState<OutcomeDistribution[]>([]);
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState(30);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchAnalyticsData = async (days: number = 30) => {
    try {
      setLoading(true);
      setError(null);

      // Fetch dashboard metrics
      const metricsResponse = await fetch(`${config.apiBaseUrl}/api/analytics/dashboard?days=${days}`);
      if (!metricsResponse.ok) {
        throw new Error('Failed to fetch dashboard metrics');
      }
      const metricsData = await metricsResponse.json();
      setMetrics(metricsData.data);

      // Fetch outcome distribution
      const outcomesResponse = await fetch(`${config.apiBaseUrl}/api/analytics/outcomes?days=${days}`);
      if (!outcomesResponse.ok) {
        throw new Error('Failed to fetch outcome distribution');
      }
      const outcomesData = await outcomesResponse.json();
      setOutcomes(outcomesData.distribution || []);

      // Fetch trends
      const trendsResponse = await fetch(`${config.apiBaseUrl}/api/analytics/trends?days=${days}`);
      if (!trendsResponse.ok) {
        throw new Error('Failed to fetch trends');
      }
      const trendsData = await trendsResponse.json();
      setTrends(trendsData.trends || []);

      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyticsData(selectedPeriod);
  }, [selectedPeriod]);

  const handleRefresh = () => {
    fetchAnalyticsData(selectedPeriod);
  };

  const handlePeriodChange = (days: number) => {
    setSelectedPeriod(days);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner />
        <span className="ml-3 text-gray-600">Loading analytics...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Failed to load analytics</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => fetchAnalyticsData(selectedPeriod)}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:ring-2 focus:ring-primary-500"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <TrendingUp className="h-8 w-8 text-primary-600 mr-3" />
            Voice Agent Analytics
          </h2>
          <p className="text-gray-600 mt-1">
            Real-time analytics powered by PIPECAT RTVI framework
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Period Selector */}
          <div className="flex items-center space-x-2">
            <Calendar className="h-4 w-4 text-gray-500" />
            <select
              value={selectedPeriod}
              onChange={(e) => handlePeriodChange(Number(e.target.value))}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:ring-primary-500 focus:border-primary-500"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
          </div>
          
          {/* Refresh Button */}
          <button
            onClick={handleRefresh}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Last Updated */}
      {lastUpdated && (
        <p className="text-sm text-gray-500">
          Last updated: {lastUpdated.toLocaleString()}
        </p>
      )}

      {/* Metrics Cards */}
      {metrics && <AnalyticsMetrics metrics={metrics} />}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Call Outcomes Chart */}
        <CallOutcomeChart data={outcomes} />
        
        {/* Analytics Trends Chart */}
        <div className="lg:col-span-2">
          <AnalyticsTrendsChart data={trends} />
        </div>
      </div>

      {/* Additional Analytics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">Interruption Rate</h4>
          <p className="text-3xl font-bold text-yellow-600">
            {metrics && metrics.total_calls > 0 
              ? `${Math.round((metrics.total_interruptions / metrics.total_calls) * 100)}%`
              : '0%'
            }
          </p>
          <p className="text-sm text-gray-600 mt-1">
            {metrics?.total_interruptions || 0} total interruptions
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">Emergency Rate</h4>
          <p className="text-3xl font-bold text-red-600">
            {metrics && metrics.total_calls > 0 
              ? `${Math.round((metrics.emergency_calls / metrics.total_calls) * 100)}%`
              : '0%'
            }
          </p>
          <p className="text-sm text-gray-600 mt-1">
            {metrics?.emergency_calls || 0} emergency calls
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">Token Efficiency</h4>
          <p className="text-3xl font-bold text-purple-600">
            {metrics?.avg_tokens_per_call?.toFixed(0) || '0'}
          </p>
          <p className="text-sm text-gray-600 mt-1">
            avg tokens per call
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">Call Quality</h4>
          <p className="text-3xl font-bold text-green-600">
            {metrics && metrics.total_calls > 0 
              ? `${Math.round((metrics.successful_calls / metrics.total_calls) * 100)}%`
              : '0%'
            }
          </p>
          <p className="text-sm text-gray-600 mt-1">
            successful calls
          </p>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;