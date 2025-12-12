import React from 'react';

// --- Button ---
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'glass';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ 
  children, variant = 'primary', size = 'md', isLoading, className = '', ...props 
}) => {
  const baseStyles = "inline-flex items-center justify-center rounded-xl font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]";
  
  const variants = {
    primary: "bg-gradient-to-br from-primary-600 to-blue-600 hover:from-primary-500 hover:to-blue-500 text-white shadow-lg shadow-primary-500/25 border border-transparent",
    secondary: "bg-white text-primary-700 hover:bg-gray-50 border border-gray-200 shadow-sm",
    outline: "border-2 border-primary-200 bg-transparent text-primary-700 hover:bg-primary-50/50 focus:ring-primary-400",
    ghost: "bg-transparent text-gray-600 hover:bg-gray-100/50 hover:text-primary-600",
    glass: "bg-white/30 backdrop-blur-md border border-white/40 text-gray-800 hover:bg-white/50 shadow-sm hover:shadow-md"
  };

  const sizes = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-5 py-2.5 text-sm",
    lg: "px-8 py-3.5 text-base",
  };

  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      ) : null}
      {children}
    </button>
  );
};

// --- Input ---
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({ label, error, className = '', ...props }) => (
  <div className="w-full">
    {label && <label className="block text-sm font-semibold text-gray-700 mb-1.5 ml-1">{label}</label>}
    <input
      className={`block w-full rounded-xl border border-white/40 bg-white/50 backdrop-blur-sm px-4 py-2.5 text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:ring-2 focus:ring-primary-200/50 focus:bg-white/80 transition-all shadow-sm ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-200' : ''} ${className}`}
      {...props}
    />
    {error && <p className="mt-1 text-xs text-red-600 font-medium ml-1">{error}</p>}
  </div>
);

// --- Card ---
// Updated for Glassmorphism
export const Card: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`bg-white/70 backdrop-blur-xl border border-white/50 shadow-xl shadow-gray-200/40 rounded-2xl ${className}`}>
    {children}
  </div>
);

// --- Badge ---
export const Badge: React.FC<{ children: React.ReactNode; variant?: 'primary' | 'secondary' | 'neutral' | 'outline' }> = ({ children, variant = 'primary' }) => {
  const styles = {
    primary: "bg-primary-100/80 text-primary-700 border border-primary-200/50 backdrop-blur-sm",
    secondary: "bg-sky-100/80 text-sky-700 border border-sky-200/50 backdrop-blur-sm",
    neutral: "bg-gray-100/80 text-gray-700 border border-gray-200/50 backdrop-blur-sm",
    outline: "border border-gray-300 text-gray-600 bg-transparent"
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold ${styles[variant]}`}>
      {children}
    </span>
  );
};

// --- Select ---
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: { value: string | number; label: string }[];
  error?: string;
}

export const Select: React.FC<SelectProps> = ({ label, options, error, className = '', ...props }) => (
  <div className="w-full">
    {label && <label className="block text-sm font-semibold text-gray-700 mb-1.5 ml-1">{label}</label>}
    <select
      className={`block w-full rounded-xl border border-white/40 bg-white/50 backdrop-blur-sm px-4 py-2.5 text-gray-900 focus:border-primary-500 focus:ring-2 focus:ring-primary-200/50 focus:bg-white/80 transition-all shadow-sm ${error ? 'border-red-500' : ''} ${className}`}
      {...props}
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
    {error && <p className="mt-1 text-xs text-red-600 font-medium ml-1">{error}</p>}
  </div>
);