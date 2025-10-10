import React from 'react';
import { Download, Phone, ArrowLeft } from 'lucide-react';
import type { CallResult } from '../types';

interface CallResultsProps {
  callResult: CallResult;
  onNewCall: () => void;
  onBackToConfig: () => void;
}

const CallResults: React.FC<CallResultsProps> = ({ callResult, onNewCall, onBackToConfig }) => {
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const exportResults = () => {
    const data = {
      callResult,
      exportedAt: new Date().toISOString(),
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `call-result-${callResult.id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Call Results</h2>
          <div className="flex space-x-3">
            <button
              onClick={exportResults}
              className="flex items-center space-x-2 px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <Download className="h-4 w-4" />
              <span>Export</span>
            </button>
            <button
              onClick={onNewCall}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              <Phone className="h-4 w-4" />
              <span>New Call</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
          <div>
            <label className="text-sm font-medium text-gray-500">Driver</label>
            <p className="font-semibold">{callResult.callRequest.driverName}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Load Number</label>
            <p className="font-semibold">{callResult.callRequest.loadNumber}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Duration</label>
            <p className="font-semibold">{callResult.duration} seconds</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Call Type</label>
            <p className="font-semibold capitalize">{callResult.callRequest.callType} Call</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Timestamp</label>
            <p className="font-semibold">{formatTimestamp(callResult.timestamp)}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Call Outcome</label>
            <p className="font-semibold">{callResult.summary.call_outcome}</p>
          </div>
        </div>

        {/* Structured Results */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Structured Summary</h3>
          
          {/* Emergency Information (if applicable) */}
          {callResult.summary.call_outcome === 'Emergency Escalation' && (
            <div className="mb-6 p-4 border-2 border-red-200 bg-red-50 rounded-lg">
              <h4 className="font-semibold text-red-900 mb-3 flex items-center">
                <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                Emergency Details
              </h4>
              <div className="grid grid-cols-2 gap-4">
                {callResult.summary.emergency_type && (
                  <div>
                    <label className="text-sm font-medium text-red-700">Emergency Type</label>
                    <p className="font-semibold text-red-900">{callResult.summary.emergency_type}</p>
                  </div>
                )}
                {callResult.summary.safety_status && (
                  <div>
                    <label className="text-sm font-medium text-red-700">Safety Status</label>
                    <p className="font-semibold text-red-900">{callResult.summary.safety_status}</p>
                  </div>
                )}
                {callResult.summary.injury_status && (
                  <div>
                    <label className="text-sm font-medium text-red-700">Injury Status</label>
                    <p className="font-semibold text-red-900">{callResult.summary.injury_status}</p>
                  </div>
                )}
                {callResult.summary.emergency_location && (
                  <div>
                    <label className="text-sm font-medium text-red-700">Emergency Location</label>
                    <p className="font-semibold text-red-900">{callResult.summary.emergency_location}</p>
                  </div>
                )}
                {callResult.summary.load_secure !== undefined && (
                  <div>
                    <label className="text-sm font-medium text-red-700">Load Secure</label>
                    <p className="font-semibold text-red-900">{callResult.summary.load_secure ? 'Yes' : 'No'}</p>
                  </div>
                )}
                {callResult.summary.escalation_status && (
                  <div>
                    <label className="text-sm font-medium text-red-700">Escalation Status</label>
                    <p className="font-semibold text-red-900">{callResult.summary.escalation_status}</p>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {/* Normal Call Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Call Outcome */}
            <div className="border rounded-lg p-4 bg-blue-50 border-blue-200">
              <h4 className="font-semibold text-blue-900 mb-2">Call Outcome</h4>
              <p className="text-blue-800 font-medium">{callResult.summary.call_outcome}</p>
            </div>
            
            {/* Driver Status */}
            <div className="border rounded-lg p-4">
              <label className="text-sm font-medium text-gray-500">Driver Status</label>
              <p className="font-semibold text-gray-900 mt-1">{callResult.summary.driver_status || 'N/A'}</p>
            </div>
            
            {/* Current Location */}
            <div className="border rounded-lg p-4">
              <label className="text-sm font-medium text-gray-500">Current Location</label>
              <p className="font-semibold text-gray-900 mt-1">{callResult.summary.current_location || 'Not specified'}</p>
            </div>
            
            {/* ETA */}
            <div className="border rounded-lg p-4">
              <label className="text-sm font-medium text-gray-500">Estimated Arrival</label>
              <p className="font-semibold text-gray-900 mt-1">{callResult.summary.eta || 'Not provided'}</p>
            </div>
            
            {/* Delay Reason */}
            <div className={`border rounded-lg p-4 ${
              callResult.summary.delay_reason && callResult.summary.delay_reason !== 'None' 
                ? 'bg-yellow-50 border-yellow-200' 
                : 'bg-green-50 border-green-200'
            }`}>
              <label className={`text-sm font-medium ${
                callResult.summary.delay_reason && callResult.summary.delay_reason !== 'None'
                  ? 'text-yellow-700'
                  : 'text-green-700'
              }`}>
                Delay Status
              </label>
              <p className={`font-semibold mt-1 ${
                callResult.summary.delay_reason && callResult.summary.delay_reason !== 'None'
                  ? 'text-yellow-900'
                  : 'text-green-900'
              }`}>
                {callResult.summary.delay_reason === 'None' || !callResult.summary.delay_reason 
                  ? 'On Schedule' 
                  : callResult.summary.delay_reason}
              </p>
            </div>
            
            {/* Unloading Status */}
            <div className="border rounded-lg p-4">
              <label className="text-sm font-medium text-gray-500">Unloading Status</label>
              <p className="font-semibold text-gray-900 mt-1">{callResult.summary.unloading_status || 'N/A'}</p>
            </div>
            
            {/* POD Reminder */}
            <div className={`border rounded-lg p-4 ${
              callResult.summary.pod_reminder_acknowledged 
                ? 'bg-green-50 border-green-200' 
                : 'bg-gray-50 border-gray-200'
            }`}>
              <label className={`text-sm font-medium ${
                callResult.summary.pod_reminder_acknowledged ? 'text-green-700' : 'text-gray-500'
              }`}>
                POD Reminder
              </label>
              <p className={`font-semibold mt-1 ${
                callResult.summary.pod_reminder_acknowledged ? 'text-green-900' : 'text-gray-900'
              }`}>
                {callResult.summary.pod_reminder_acknowledged ? 'Acknowledged' : 'Not Mentioned'}
              </p>
            </div>
          </div>
        </div>

        {/* Full Transcript */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Full Transcript</h3>
          <div className="border rounded-lg p-4 bg-gray-50">
            <div className="h-96 overflow-y-auto font-mono text-sm whitespace-pre-wrap">
              {callResult.transcript || 'No transcript available'}
            </div>
          </div>
        </div>

        <div className="flex justify-start mt-6 pt-6 border-t">
          <button
            onClick={onBackToConfig}
            className="flex items-center space-x-2 px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Configuration</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default CallResults;