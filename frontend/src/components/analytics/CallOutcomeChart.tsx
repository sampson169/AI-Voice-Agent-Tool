import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface CallOutcomeChartProps {
  data: Array<{
    outcome: string;
    count: number;
    percentage: number;
  }>;
}

const CallOutcomeChart: React.FC<CallOutcomeChartProps> = ({ data }) => {
  const chartData = data.map(item => ({
    name: item.outcome.replace(' ', '\n'),
    count: item.count,
    percentage: item.percentage
  }));

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Call Outcomes Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="name" 
            fontSize={12}
            interval={0}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis />
          <Tooltip 
            formatter={(value: any, name: any) => [
              name === 'count' ? `${value} calls` : `${value}%`,
              name === 'count' ? 'Count' : 'Percentage'
            ]}
          />
          <Legend />
          <Bar dataKey="count" fill="#3b82f6" name="Calls" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CallOutcomeChart;