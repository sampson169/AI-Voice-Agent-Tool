import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface ScenarioCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  isSelected: boolean;
  onClick: () => void;
  variant?: 'default' | 'success' | 'warning' | 'danger';
  className?: string;
}

const ScenarioCard: React.FC<ScenarioCardProps> = ({
  title,
  description,
  icon: Icon,
  isSelected,
  onClick,
  variant = 'default',
  className = ''
}) => {
  const getVariantClasses = () => {
    const base = 'p-4 border rounded-lg text-left transition-colors hover:bg-opacity-50';
    
    if (isSelected) {
      switch (variant) {
        case 'success':
          return `${base} border-green-500 bg-green-50 ring-2 ring-green-200`;
        case 'warning':
          return `${base} border-yellow-500 bg-yellow-50 ring-2 ring-yellow-200`;
        case 'danger':
          return `${base} border-red-500 bg-red-50 ring-2 ring-red-200`;
        default:
          return `${base} border-blue-500 bg-blue-50 ring-2 ring-blue-200`;
      }
    }
    
    switch (variant) {
      case 'success':
        return `${base} border-gray-300 hover:border-green-500 hover:bg-green-50`;
      case 'warning':
        return `${base} border-gray-300 hover:border-yellow-500 hover:bg-yellow-50`;
      case 'danger':
        return `${base} border-gray-300 hover:border-red-500 hover:bg-red-50`;
      default:
        return `${base} border-gray-300 hover:border-blue-500 hover:bg-blue-50`;
    }
  };

  const getIconColor = () => {
    if (isSelected) {
      switch (variant) {
        case 'success': return 'text-green-700';
        case 'warning': return 'text-yellow-700';
        case 'danger': return 'text-red-700';
        default: return 'text-blue-700';
      }
    }
    
    switch (variant) {
      case 'success': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'danger': return 'text-red-600';
      default: return 'text-blue-600';
    }
  };

  const getTitleColor = () => {
    if (isSelected) {
      switch (variant) {
        case 'success': return 'text-green-900';
        case 'warning': return 'text-yellow-900';
        case 'danger': return 'text-red-900';
        default: return 'text-blue-900';
      }
    }
    return 'text-gray-900';
  };

  const getBadgeClasses = () => {
    switch (variant) {
      case 'success': return 'bg-green-100 text-green-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      case 'danger': return 'bg-red-100 text-red-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  return (
    <button
      type="button"
      onClick={onClick}
      className={`${getVariantClasses()} ${className}`}
      aria-pressed={isSelected}
    >
      <div className="flex items-start space-x-3">
        <Icon className={`h-5 w-5 mt-0.5 flex-shrink-0 ${getIconColor()}`} aria-hidden="true" />
        <div className="flex-1 min-w-0">
          <h4 className={`font-semibold mb-2 ${getTitleColor()}`}>
            {title}
            {isSelected && (
              <span className={`ml-2 text-xs px-2 py-1 rounded-full ${getBadgeClasses()}`}>
                SELECTED
              </span>
            )}
          </h4>
          <p className="text-sm text-gray-600">
            {description}
          </p>
        </div>
      </div>
    </button>
  );
};

export default ScenarioCard;