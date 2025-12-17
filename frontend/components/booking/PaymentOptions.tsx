/**
 * Payment Options Component
 * Displays available payment methods (UPI, Cards)
 */

import React from 'react';
import { Smartphone, CreditCard, Building2, Wallet } from 'lucide-react';

type PaymentMethod = 'upi' | 'card' | 'netbanking' | 'wallet';

interface PaymentOption {
  id: PaymentMethod;
  name: string;
  description: string;
  icon: React.ReactNode;
  popular?: boolean;
}

const paymentOptions: PaymentOption[] = [
  {
    id: 'upi',
    name: 'UPI',
    description: 'Pay using any UPI app',
    icon: <Smartphone size={24} />,
    popular: true,
  },
  {
    id: 'card',
    name: 'Credit/Debit Card',
    description: 'Visa, Mastercard, RuPay',
    icon: <CreditCard size={24} />,
  },
  {
    id: 'netbanking',
    name: 'Net Banking',
    description: 'All major banks supported',
    icon: <Building2 size={24} />,
  },
  {
    id: 'wallet',
    name: 'Wallets',
    description: 'Paytm, PhonePe, etc.',
    icon: <Wallet size={24} />,
  },
];

interface PaymentOptionsProps {
  selectedMethod?: PaymentMethod;
  onMethodSelect: (method: PaymentMethod) => void;
}

const PaymentOptions: React.FC<PaymentOptionsProps> = ({
  selectedMethod,
  onMethodSelect,
}) => {
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold text-gray-700 mb-3">
        Choose Payment Method
      </h4>

      {paymentOptions.map((option) => (
        <button
          key={option.id}
          onClick={() => onMethodSelect(option.id)}
          className={`
            w-full flex items-center gap-4 p-4 rounded-xl
            border-2 transition-all duration-200
            ${
              selectedMethod === option.id
                ? 'border-primary-500 bg-primary-50 shadow-lg shadow-primary-500/10'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            }
          `}
        >
          {/* Icon */}
          <div
            className={`
            p-3 rounded-xl
            ${
              selectedMethod === option.id
                ? 'bg-primary-500 text-white'
                : 'bg-gray-100 text-gray-600'
            }
          `}
          >
            {option.icon}
          </div>

          {/* Content */}
          <div className="flex-1 text-left">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-gray-900">{option.name}</span>
              {option.popular && (
                <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full font-medium">
                  Popular
                </span>
              )}
            </div>
            <p className="text-sm text-gray-500">{option.description}</p>
          </div>

          {/* Radio indicator */}
          <div
            className={`
            w-5 h-5 rounded-full border-2 flex items-center justify-center
            ${
              selectedMethod === option.id
                ? 'border-primary-500 bg-primary-500'
                : 'border-gray-300'
            }
          `}
          >
            {selectedMethod === option.id && (
              <div className="w-2 h-2 bg-white rounded-full" />
            )}
          </div>
        </button>
      ))}

      {/* Security Note */}
      <div className="mt-4 p-3 bg-gray-50 rounded-xl">
        <p className="text-xs text-gray-500 text-center">
          Secured by Razorpay. Your payment information is encrypted and secure.
        </p>
      </div>
    </div>
  );
};

export default PaymentOptions;
