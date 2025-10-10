import React from 'react';
import { Truck, Settings, Phone, BarChart3 } from 'lucide-react';
import type { AppView, AgentConfig } from '../types';

interface DashboardProps {
  currentView: AppView;
  onViewChange: (view: AppView) => void;
  agentConfig: AgentConfig | null;
}

const Dashboard: React.FC<DashboardProps> = ({ currentView, onViewChange, agentConfig }) => {
  const navItems = [
    { id: 'config' as AppView, label: 'Agent Configuration', icon: Settings },
    { id: 'call' as AppView, label: 'Make Call', icon: Phone },
    { id: 'results' as AppView, label: 'Call Results', icon: BarChart3 },
  ];

  return (
    <nav className="bg-white shadow-lg border-b">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3">
            <Truck className="h-8 w-8 text-primary-600" />
            <h1 className="text-xl font-bold text-gray-900">AI Voice Agent Tool</h1>
          </div>
          
          <div className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              const isDisabled = item.id === 'call' && !agentConfig;
              
              return (
                <button
                  key={item.id}
                  onClick={() => !isDisabled && onViewChange(item.id)}
                  disabled={isDisabled}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                    isActive
                      ? 'bg-primary-100 text-primary-700 border border-primary-300'
                      : isDisabled
                      ? 'text-gray-400 cursor-not-allowed'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Dashboard;