import React, { useEffect } from 'react';
import { Portal } from './Portal';

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
// Updated for Glassmorphism with full div props support
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ children, className = '', ...props }) => (
  <div
    className={`bg-white/70 backdrop-blur-xl border border-white/50 shadow-xl shadow-gray-200/40 rounded-2xl ${className}`}
    {...props}
  >
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

// --- Modal ---
// Reusable modal component with Portal-based rendering for proper positioning
// Uses React Portal to render outside the DOM hierarchy, preventing z-index
// and overflow issues with navigation bars and parent containers
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  closeOnBackdropClick?: boolean;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  children,
  maxWidth = 'lg',
  closeOnBackdropClick = true,
}) => {
  // Lock body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const maxWidthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
  };

  const handleBackdropClick = () => {
    if (closeOnBackdropClick) {
      onClose();
    }
  };

  return (
    <Portal>
      {/* Modal Overlay - uses fixed positioning relative to viewport */}
      <div
        className="fixed inset-0 z-[9999] flex items-center justify-center"
        style={{ margin: 0, padding: 0 }}
      >
        {/* Backdrop */}
        <div
          className="absolute inset-0 bg-black/50 backdrop-blur-sm"
          onClick={handleBackdropClick}
        />

        {/* Modal Container - centered using flex */}
        <div
          className={`
            relative w-full ${maxWidthClasses[maxWidth]}
            bg-white rounded-2xl shadow-2xl
            mx-4 max-h-[90vh] overflow-y-auto
            animate-modal-scale-in
          `}
          onClick={(e) => e.stopPropagation()}
        >
          {children}
        </div>
      </div>

      {/* Animation Styles */}
      <style>{`
        @keyframes modalScaleIn {
          from {
            opacity: 0;
            transform: scale(0.95);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        .animate-modal-scale-in {
          animation: modalScaleIn 0.2s ease-out forwards;
        }
      `}</style>
    </Portal>
  );
};

// Modal sub-components for consistent structure
interface ModalHeaderProps {
  children: React.ReactNode;
  onClose?: () => void;
  className?: string;
}

export const ModalHeader: React.FC<ModalHeaderProps> = ({ children, onClose, className = '' }) => (
  <div className={`sticky top-0 z-10 flex items-center justify-between p-6 border-b border-gray-100 bg-white ${className}`}>
    <div className="flex-1">{children}</div>
    {onClose && (
      <button
        onClick={onClose}
        className="p-2 rounded-xl hover:bg-gray-100 transition-colors ml-4"
      >
        <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    )}
  </div>
);

interface ModalBodyProps {
  children: React.ReactNode;
  className?: string;
}

export const ModalBody: React.FC<ModalBodyProps> = ({ children, className = '' }) => (
  <div className={`p-6 ${className}`}>{children}</div>
);

interface ModalFooterProps {
  children: React.ReactNode;
  className?: string;
}

export const ModalFooter: React.FC<ModalFooterProps> = ({ children, className = '' }) => (
  <div className={`p-6 border-t border-gray-100 bg-gray-50 ${className}`}>{children}</div>
);