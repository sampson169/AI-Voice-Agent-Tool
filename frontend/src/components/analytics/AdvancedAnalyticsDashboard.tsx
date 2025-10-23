import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
         LineChart, Line, PieChart, Pie, Cell, ScatterChart, Scatter } from 'recharts';
import { Calendar, TrendingUp, Activity, Clock, Users, Phone } from 'lucide-react';
import LoadingSpinner from '../ui/LoadingSpinner';
import config from '../../utils/config';

interface HeatmapData {
  hour: number;
  day: string;
  calls: number;
  quality_score: number;
  emergency_rate: number;
}

interface PerformanceMetrics {
  agent_id: string;
  agent_name: string;
  total_calls: number;
  avg_quality_score: number;
  avg_duration: number;
  emergency_handling_score: number;
  customer_satisfaction: number;
  efficiency_score: number;
}

interface PredictiveData {
  date: string;
  predicted_calls: number;
  predicted_emergencies: number;
  confidence_interval: [number, number];
}

interface TrendData {
  date: string;
  calls: number;
  quality: number;
  duration: number;
  emergencies: number;
  satisfaction: number;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const AdvancedAnalyticsDashboard: React.FC = () => {
  const [heatmapData, setHeatmapData] = useState<HeatmapData[]>([]);
  const [performanceData, setPerformanceData] = useState<PerformanceMetrics[]>([]);
  const [predictiveData, setPredictiveData] = useState<PredictiveData[]>([]);
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(30);
  const [selectedView, setSelectedView] = useState<'heatmap' | 'performance' | 'predictions' | 'trends'>('heatmap');

  const fetchAdvancedAnalytics = async (days: number = 30) => {
    try {
      setLoading(true);

      // Fetch heatmap data
      const heatmapResponse = await fetch(`${config.apiBaseUrl}/api/analytics/heatmap?days=${days}`);
      if (heatmapResponse.ok) {
        const heatmapResult = await heatmapResponse.json();
        setHeatmapData(heatmapResult.data || []);
      }

      const performanceResponse = await fetch(`${config.apiBaseUrl}/api/analytics/performance?days=${days}`);
      if (performanceResponse.ok) {
        const performanceResult = await performanceResponse.json();
        setPerformanceData(performanceResult.data || []);
      }

      const predictiveResponse = await fetch(`${config.apiBaseUrl}/api/analytics/predictions?days=14`);
      if (predictiveResponse.ok) {
        const predictiveResult = await predictiveResponse.json();
        setPredictiveData(predictiveResult.data || []);
      }

      const trendResponse = await fetch(`${config.apiBaseUrl}/api/analytics/trends?days=${days}`);
      if (trendResponse.ok) {
        const trendResult = await trendResponse.json();
        setTrendData(trendResult.trends || []);
      }

    } catch (error) {
      console.error('Error fetching advanced analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdvancedAnalytics(selectedPeriod);
  }, [selectedPeriod]);

  const renderHeatmap = () => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const hours = Array.from({ length: 24 }, (_, i) => i);

    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Call Volume Heatmap</h3>
        <div className="overflow-x-auto">
          <div className="grid grid-cols-25 gap-1 min-w-max">
            {/* Header row with hours */}
            <div className="text-xs font-medium text-gray-500 p-1"></div>
            {hours.map(hour => (
              <div key={hour} className="text-xs font-medium text-gray-500 p-1 text-center">
                {hour}
              </div>
            ))}
            
            {/* Data rows */}
            {days.map(day => (
              <React.Fragment key={day}>
                <div className="text-xs font-medium text-gray-500 p-2 text-right">{day}</div>
                {hours.map(hour => {
                  const dataPoint = heatmapData.find(d => d.day === day && d.hour === hour);
                  const intensity = dataPoint ? Math.min(dataPoint.calls / 10, 1) : 0;
                  const bgColor = `rgba(59, 130, 246, ${intensity})`;
                  
                  return (
                    <div
                      key={`${day}-${hour}`}
                      className="w-8 h-8 rounded border border-gray-200 flex items-center justify-center text-xs font-medium cursor-pointer hover:border-blue-500"
                      style={{ backgroundColor: bgColor }}
                      title={`${day} ${hour}:00 - ${dataPoint?.calls || 0} calls`}
                    >
                      {dataPoint?.calls || 0}
                    </div>
                  );
                })}
              </React.Fragment>
            ))}
          </div>
        </div>
        <div className="flex items-center justify-between mt-4 text-xs text-gray-500">
          <span>Low Activity</span>
          <div className="flex items-center space-x-1">
            {[0.2, 0.4, 0.6, 0.8, 1.0].map(intensity => (
              <div
                key={intensity}
                className="w-4 h-4 rounded border border-gray-200"
                style={{ backgroundColor: `rgba(59, 130, 246, ${intensity})` }}
              />
            ))}
          </div>
          <span>High Activity</span>
        </div>
      </div>
    );
  };

  const renderPerformanceMetrics = () => (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Agent Performance</h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quality Score vs Call Volume */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Quality vs Volume</h4>
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="total_calls" name="Total Calls" />
              <YAxis dataKey="avg_quality_score" name="Quality Score" />
              <Tooltip formatter={(value, name) => [value, name]} />
              <Scatter dataKey="avg_quality_score" fill="#8884d8" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* Performance Radar */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Performance Metrics</h4>
          <div className="space-y-4">
            {performanceData.slice(0, 5).map((agent, index) => (
              <div key={agent.agent_id} className="border rounded-lg p-4">
                <h5 className="font-medium text-gray-900 mb-2">{agent.agent_name}</h5>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Quality Score:</span>
                    <div className="flex items-center mt-1">
                      <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className="h-2 bg-blue-600 rounded-full"
                          style={{ width: `${agent.avg_quality_score * 100}%` }}
                        />
                      </div>
                      <span className="font-medium">{(agent.avg_quality_score * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-600">Efficiency:</span>
                    <div className="flex items-center mt-1">
                      <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className="h-2 bg-green-600 rounded-full"
                          style={{ width: `${agent.efficiency_score * 100}%` }}
                        />
                      </div>
                      <span className="font-medium">{(agent.efficiency_score * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-600">Emergency Handling:</span>
                    <div className="flex items-center mt-1">
                      <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className="h-2 bg-red-600 rounded-full"
                          style={{ width: `${agent.emergency_handling_score * 100}%` }}
                        />
                      </div>
                      <span className="font-medium">{(agent.emergency_handling_score * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-600">Total Calls:</span>
                    <span className="font-medium ml-2">{agent.total_calls}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderPredictiveAnalytics = () => (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Predictive Analytics</h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Predicted Call Volume</h4>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={predictiveData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="predicted_calls" stroke="#8884d8" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Emergency Predictions */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Emergency Likelihood</h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={predictiveData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="predicted_emergencies" fill="#ff6b6b" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h5 className="font-medium text-blue-900">Peak Hours</h5>
          <p className="text-sm text-blue-700 mt-1">
            Highest call volume predicted between 2-4 PM on weekdays
          </p>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg">
          <h5 className="font-medium text-yellow-900">Resource Planning</h5>
          <p className="text-sm text-yellow-700 mt-1">
            Consider adding 2 additional agents during peak hours
          </p>
        </div>
        <div className="bg-red-50 p-4 rounded-lg">
          <h5 className="font-medium text-red-900">Emergency Forecast</h5>
          <p className="text-sm text-red-700 mt-1">
            15% higher emergency rate expected this Friday
          </p>
        </div>
      </div>
    </div>
  );

  const renderTrendAnalysis = () => (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Trend Analysis</h3>
      <div className="space-y-6">
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Key Metrics Over Time</h4>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Line yAxisId="left" type="monotone" dataKey="calls" stroke="#8884d8" name="Calls" />
              <Line yAxisId="right" type="monotone" dataKey="quality" stroke="#82ca9d" name="Quality %" />
              <Line yAxisId="left" type="monotone" dataKey="duration" stroke="#ffc658" name="Avg Duration" />
              <Line yAxisId="left" type="monotone" dataKey="emergencies" stroke="#ff7300" name="Emergencies" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <TrendingUp className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-900">Call Volume</p>
            <p className="text-lg font-bold text-green-600">+12%</p>
            <p className="text-xs text-gray-500">vs last period</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <Activity className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-900">Quality Score</p>
            <p className="text-lg font-bold text-blue-600">+8%</p>
            <p className="text-xs text-gray-500">vs last period</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <Clock className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-900">Avg Duration</p>
            <p className="text-lg font-bold text-yellow-600">-5%</p>
            <p className="text-xs text-gray-500">vs last period</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <Phone className="h-8 w-8 text-red-600 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-900">Emergency Rate</p>
            <p className="text-lg font-bold text-red-600">-15%</p>
            <p className="text-xs text-gray-500">vs last period</p>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner />
        <span className="ml-3 text-gray-600">Loading advanced analytics...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Advanced Analytics</h2>
          <p className="text-gray-600 mt-1">Deep insights and predictive analytics</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(Number(e.target.value))}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-primary-500 focus:border-primary-500"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>
      </div>

      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: 'heatmap', label: 'Activity Heatmap', icon: Calendar },
            { key: 'performance', label: 'Performance', icon: TrendingUp },
            { key: 'predictions', label: 'Predictions', icon: Activity },
            { key: 'trends', label: 'Trends', icon: Clock }
          ].map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setSelectedView(key as any)}
              className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                selectedView === key
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Icon className="h-4 w-4 mr-2" />
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      {selectedView === 'heatmap' && renderHeatmap()}
      {selectedView === 'performance' && renderPerformanceMetrics()}
      {selectedView === 'predictions' && renderPredictiveAnalytics()}
      {selectedView === 'trends' && renderTrendAnalysis()}
    </div>
  );
};

export default AdvancedAnalyticsDashboard;