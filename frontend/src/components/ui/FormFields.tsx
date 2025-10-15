import React from 'react';

interface BaseFieldProps {
  label?: string;
  error?: string;
  required?: boolean;
  className?: string;
  helpText?: string;
}

interface TextFieldProps extends BaseFieldProps, React.InputHTMLAttributes<HTMLInputElement> {
  type?: 'text' | 'email' | 'tel' | 'password';
}

interface TextAreaProps extends BaseFieldProps, React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

interface SelectFieldProps extends BaseFieldProps, React.SelectHTMLAttributes<HTMLSelectElement> {
  options: Array<{ value: string; label: string }>;
  placeholder?: string;
}

const FieldWrapper: React.FC<{ 
  label?: string; 
  error?: string; 
  required?: boolean; 
  className?: string;
  helpText?: string;
  children: React.ReactNode;
}> = ({ label, error, required, className = '', helpText, children }) => (
  <div className={`space-y-1 ${className}`}>
    {label && (
      <label className="block text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
    )}
    {children}
    {helpText && !error && (
      <p className="text-sm text-gray-500">{helpText}</p>
    )}
    {error && (
      <p className="text-sm text-red-600" role="alert">{error}</p>
    )}
  </div>
);

export const TextField: React.FC<TextFieldProps> = ({
  label,
  error,
  required,
  className = '',
  helpText,
  type = 'text',
  ...props
}) => {
  const inputClasses = `block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
    error 
      ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
      : 'border-gray-300'
  }`;

  return (
    <FieldWrapper 
      label={label} 
      error={error} 
      required={required} 
      className={className}
      helpText={helpText}
    >
      <input
        type={type}
        className={inputClasses}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? `${props.id}-error` : undefined}
        {...props}
      />
    </FieldWrapper>
  );
};

export const TextArea: React.FC<TextAreaProps> = ({
  label,
  error,
  required,
  className = '',
  helpText,
  ...props
}) => {
  const textareaClasses = `block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
    error 
      ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
      : 'border-gray-300'
  }`;

  return (
    <FieldWrapper 
      label={label} 
      error={error} 
      required={required} 
      className={className}
      helpText={helpText}
    >
      <textarea
        className={textareaClasses}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? `${props.id}-error` : undefined}
        {...props}
      />
    </FieldWrapper>
  );
};

export const SelectField: React.FC<SelectFieldProps> = ({
  label,
  error,
  required,
  className = '',
  helpText,
  options,
  placeholder,
  ...props
}) => {
  const selectClasses = `block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
    error 
      ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
      : 'border-gray-300'
  }`;

  return (
    <FieldWrapper 
      label={label} 
      error={error} 
      required={required} 
      className={className}
      helpText={helpText}
    >
      <select
        className={selectClasses}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? `${props.id}-error` : undefined}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </FieldWrapper>
  );
};