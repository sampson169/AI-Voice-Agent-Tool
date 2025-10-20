import { useState } from 'react';
import Dashboard from './components/Dashboard';
import AgentConfiguration from './components/AgentConfiguration';
import CallInterface from './components/CallInterface';
import CallResults from './components/CallResults';
import AnalyticsDashboard from './components/analytics/AnalyticsDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import type { AppView, AgentConfig, CallResult } from './types';

function App() {
  const [currentView, setCurrentView] = useState<AppView>('config');
  const [agentConfig, setAgentConfig] = useState<AgentConfig | null>(null);
  const [callResult, setCallResult] = useState<CallResult | null>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      <Dashboard 
        currentView={currentView} 
        onViewChange={setCurrentView}
        agentConfig={agentConfig}
      />
      
      <div className="container mx-auto px-4 py-8">
        <ErrorBoundary>
          {currentView === 'config' && (
            <AgentConfiguration 
              onConfigSave={setAgentConfig}
              onStartCall={() => setCurrentView('call')}
            />
          )}
          
          {currentView === 'call' && agentConfig && (
            <CallInterface 
              agentConfig={agentConfig}
              onCallEnd={(result) => {
                setCallResult(result);
                setCurrentView('results');
              }}
              onBack={() => setCurrentView('config')}
            />
          )}
          
          {currentView === 'results' && callResult && (
            <CallResults 
              callResult={callResult}
              onNewCall={() => setCurrentView('call')}
              onBackToConfig={() => setCurrentView('config')}
            />
          )}
          
          {currentView === 'analytics' && (
            <AnalyticsDashboard />
          )}
        </ErrorBoundary>
      </div>
    </div>
  );
}

export default App;