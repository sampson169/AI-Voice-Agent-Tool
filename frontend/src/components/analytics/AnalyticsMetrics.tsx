import React from 'react';
import { Phone, Clock, AlertTriangle, Zap, CheckCircle } from 'lucide-react';

interface AnalyticsMetricsProps {
  metrics: {
    total_calls: number;
    avg_call_duration: number;
    total_interruptions: number;
    total_tokens: number;
    avg_tokens_per_call: number;
    emergency_calls: number;
    successful_calls: number;
  };
}

const AnalyticsMetrics: React.FC<AnalyticsMetricsProps> = ({ metrics }) => {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };

  const cards = [
    {
      title: 'Total Calls',
      value: metrics.total_calls,
      icon: Phone,
      color: 'bg-blue-500',
      textColor: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      title: 'Avg Call Duration',
      value: formatDuration(metrics.avg_call_duration),
      icon: Clock,
      color: 'bg-green-500',
      textColor: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      title: 'Total Interruptions',
      value: metrics.total_interruptions,
      icon: AlertTriangle,
      color: 'bg-yellow-500',
      textColor: 'text-yellow-600',
      bgColor: 'bg-yellow-50'
    },
    {
      title: 'Emergency Calls',
      value: metrics.emergency_calls,
      icon: AlertTriangle,
      color: 'bg-red-500',
      textColor: 'text-red-600',
      bgColor: 'bg-red-50'
    },
    {
      title: 'Total Tokens',
      value: formatNumber(metrics.total_tokens),
      icon: Zap,
      color: 'bg-purple-500',
      textColor: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      title: 'Success Rate',
      value: metrics.total_calls > 0 ? `${Math.round((metrics.successful_calls / metrics.total_calls) * 100)}%` : '0%',
      icon: CheckCircle,
      color: 'bg-emerald-500',
      textColor: 'text-emerald-600',
      bgColor: 'bg-emerald-50'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <div key={index} className={`${card.bgColor} p-6 rounded-lg shadow-md`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">{card.title}</p>
                <p className={`text-2xl font-bold ${card.textColor}`}>{card.value}</p>
              </div>
              <div className={`${card.color} p-3 rounded-full`}>
                <Icon className="h-6 w-6 text-white" />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default AnalyticsMetrics;