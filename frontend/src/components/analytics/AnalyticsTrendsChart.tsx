import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface AnalyticsTrendsChartProps {
  data: Array<{
    date: string;
    total_calls: number;
    avg_duration: number;
    interruptions: number;
    emergency_calls: number;
    tokens_used: number;
  }>;
}

const AnalyticsTrendsChart: React.FC<AnalyticsTrendsChartProps> = ({ data }) => {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const chartData = data.map(item => ({
    ...item,
    date: formatDate(item.date),
    avg_duration: Math.round(item.avg_duration * 10) / 10
  }));

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Analytics Trends</h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip 
            formatter={(value: any, name: any) => {
              switch (name) {
                case 'total_calls':
                  return [`${value} calls`, 'Total Calls'];
                case 'avg_duration':
                  return [`${value}s`, 'Avg Duration'];
                case 'interruptions':
                  return [`${value}`, 'Interruptions'];
                case 'emergency_calls':
                  return [`${value}`, 'Emergency Calls'];
                case 'tokens_used':
                  return [`${value}`, 'Tokens Used'];
                default:
                  return [value, name];
              }
            }}
          />
          <Legend />
          <Line 
            yAxisId="left"
            type="monotone" 
            dataKey="total_calls" 
            stroke="#3b82f6" 
            strokeWidth={2}
            name="Total Calls"
          />
          <Line 
            yAxisId="left"
            type="monotone" 
            dataKey="avg_duration" 
            stroke="#10b981" 
            strokeWidth={2}
            name="Avg Duration (s)"
          />
          <Line 
            yAxisId="left"
            type="monotone" 
            dataKey="interruptions" 
            stroke="#f59e0b" 
            strokeWidth={2}
            name="Interruptions"
          />
          <Line 
            yAxisId="left"
            type="monotone" 
            dataKey="emergency_calls" 
            stroke="#ef4444" 
            strokeWidth={2}
            name="Emergency Calls"
          />
          <Line 
            yAxisId="right"
            type="monotone" 
            dataKey="tokens_used" 
            stroke="#8b5cf6" 
            strokeWidth={2}
            name="Tokens Used"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AnalyticsTrendsChart;