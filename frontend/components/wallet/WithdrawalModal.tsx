/**
 * Withdrawal Modal Component
 * Modal with tabs for different payment methods: Bank Transfer, Payoneer, Razorpay, UPI
 */

import React, { useState } from 'react';
import {
  X,
  Building2,
  CreditCard,
  Smartphone,
  ArrowDownToLine,
  AlertCircle,
  CheckCircle,
  Loader2,
} from 'lucide-react';
import { Button, Input } from '../UIComponents';
import api from '../../lib/axios';

interface WithdrawalModalProps {
  isOpen: boolean;
  onClose: () => void;
  balance: number;
  onSuccess: () => void;
}

type PaymentMethod = 'bank_transfer' | 'payoneer' | 'razorpay' | 'upi';

interface PaymentTab {
  id: PaymentMethod;
  name: string;
  icon: React.ReactNode;
  description: string;
}

const paymentTabs: PaymentTab[] = [
  {
    id: 'bank_transfer',
    name: 'Bank Transfer',
    icon: <Building2 size={20} />,
    description: 'Direct transfer to your bank account',
  },
  {
    id: 'payoneer',
    name: 'Payoneer',
    icon: <CreditCard size={20} />,
    description: 'Withdraw to your Payoneer account',
  },
  {
    id: 'razorpay',
    name: 'Razorpay',
    icon: <CreditCard size={20} />,
    description: 'Fast payout via Razorpay',
  },
  {
    id: 'upi',
    name: 'UPI',
    icon: <Smartphone size={20} />,
    description: 'Instant transfer to UPI ID',
  },
];

const WithdrawalModal: React.FC<WithdrawalModalProps> = ({
  isOpen,
  onClose,
  balance,
  onSuccess,
}) => {
  const [activeTab, setActiveTab] = useState<PaymentMethod>('bank_transfer');
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Bank Transfer fields
  const [bankName, setBankName] = useState('');
  const [accountNumber, setAccountNumber] = useState('');
  const [ifscCode, setIfscCode] = useState('');
  const [accountHolderName, setAccountHolderName] = useState('');

  // Payoneer fields
  const [payoneerEmail, setPayoneerEmail] = useState('');

  // UPI fields
  const [upiId, setUpiId] = useState('');

  // Razorpay fields
  const [razorpayAccountId, setRazorpayAccountId] = useState('');

  if (!isOpen) return null;

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getPaymentDetails = (): Record<string, string> => {
    switch (activeTab) {
      case 'bank_transfer':
        return {
          bank_name: bankName,
          account_number: accountNumber,
          ifsc_code: ifscCode,
          account_holder_name: accountHolderName,
        };
      case 'payoneer':
        return { payoneer_email: payoneerEmail };
      case 'upi':
        return { upi_id: upiId };
      case 'razorpay':
        return { razorpay_account_id: razorpayAccountId };
      default:
        return {};
    }
  };

  const validateForm = (): boolean => {
    const withdrawAmount = parseFloat(amount);
    if (!amount || isNaN(withdrawAmount) || withdrawAmount <= 0) {
      setError('Please enter a valid amount');
      return false;
    }
    if (withdrawAmount > balance) {
      setError('Amount exceeds available balance');
      return false;
    }
    if (withdrawAmount < 100) {
      setError('Minimum withdrawal amount is ₹100');
      return false;
    }

    switch (activeTab) {
      case 'bank_transfer':
        if (!bankName || !accountNumber || !ifscCode || !accountHolderName) {
          setError('Please fill in all bank details');
          return false;
        }
        break;
      case 'payoneer':
        if (!payoneerEmail) {
          setError('Please enter your Payoneer email');
          return false;
        }
        break;
      case 'upi':
        if (!upiId) {
          setError('Please enter your UPI ID');
          return false;
        }
        break;
      case 'razorpay':
        if (!razorpayAccountId) {
          setError('Please enter your Razorpay account ID');
          return false;
        }
        break;
    }

    return true;
  };

  const handleWithdraw = async () => {
    setError('');
    if (!validateForm()) return;

    try {
      setLoading(true);
      await api.post('/wallet/withdraw', {
        amount: parseFloat(amount),
        payment_method: activeTab,
        payment_details: getPaymentDetails(),
      });
      setSuccess(true);
      setTimeout(() => {
        onSuccess();
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process withdrawal');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setAmount('');
    setError('');
    setSuccess(false);
    setBankName('');
    setAccountNumber('');
    setIfscCode('');
    setAccountHolderName('');
    setPayoneerEmail('');
    setUpiId('');
    setRazorpayAccountId('');
    onClose();
  };

  const renderPaymentFields = () => {
    switch (activeTab) {
      case 'bank_transfer':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bank Name
              </label>
              <Input
                type="text"
                placeholder="e.g., HDFC Bank"
                value={bankName}
                onChange={(e) => setBankName(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Account Holder Name
              </label>
              <Input
                type="text"
                placeholder="As per bank records"
                value={accountHolderName}
                onChange={(e) => setAccountHolderName(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Account Number
              </label>
              <Input
                type="text"
                placeholder="Enter account number"
                value={accountNumber}
                onChange={(e) => setAccountNumber(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                IFSC Code
              </label>
              <Input
                type="text"
                placeholder="e.g., HDFC0001234"
                value={ifscCode}
                onChange={(e) => setIfscCode(e.target.value.toUpperCase())}
              />
            </div>
          </div>
        );

      case 'payoneer':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Payoneer Email
              </label>
              <Input
                type="email"
                placeholder="your@payoneer-email.com"
                value={payoneerEmail}
                onChange={(e) => setPayoneerEmail(e.target.value)}
              />
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <p className="text-sm text-blue-700">
                Make sure your Payoneer account is verified and can receive INR payments.
                Processing time: 2-3 business days.
              </p>
            </div>
          </div>
        );

      case 'upi':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                UPI ID
              </label>
              <Input
                type="text"
                placeholder="yourname@upi"
                value={upiId}
                onChange={(e) => setUpiId(e.target.value)}
              />
            </div>
            <div className="bg-green-50 border border-green-200 rounded-xl p-4">
              <p className="text-sm text-green-700">
                UPI transfers are instant! Make sure your UPI ID is correct.
                Maximum limit: ₹1,00,000 per transaction.
              </p>
            </div>
          </div>
        );

      case 'razorpay':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Razorpay Account ID
              </label>
              <Input
                type="text"
                placeholder="acc_xxxxxxxxx"
                value={razorpayAccountId}
                onChange={(e) => setRazorpayAccountId(e.target.value)}
              />
            </div>
            <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
              <p className="text-sm text-purple-700">
                Link your Razorpay account for fast payouts.
                Processing time: Within 24 hours.
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-lg mx-4 bg-white rounded-2xl shadow-2xl overflow-hidden animate-slideDown">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gradient-to-r from-emerald-50 to-green-50">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Withdraw Funds</h2>
            <p className="text-sm text-gray-600 mt-1">
              Available balance: <span className="font-semibold text-emerald-600">{formatCurrency(balance)}</span>
            </p>
          </div>
          <button
            onClick={handleClose}
            className="p-2 rounded-xl hover:bg-white/80 transition-colors"
          >
            <X size={20} className="text-gray-500" />
          </button>
        </div>

        {success ? (
          /* Success State */
          <div className="p-8 text-center">
            <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle size={32} className="text-green-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Withdrawal Requested!</h3>
            <p className="text-gray-600">
              Your withdrawal of {formatCurrency(parseFloat(amount))} has been submitted.
              You'll receive the funds within 2-3 business days.
            </p>
          </div>
        ) : (
          <>
            {/* Payment Method Tabs */}
            <div className="p-4 border-b border-gray-100">
              <div className="grid grid-cols-4 gap-2">
                {paymentTabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      flex flex-col items-center gap-1 p-3 rounded-xl transition-all duration-300
                      ${activeTab === tab.id
                        ? 'bg-gradient-to-br from-emerald-500 to-green-600 text-white shadow-lg shadow-emerald-500/30'
                        : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                      }
                    `}
                  >
                    {tab.icon}
                    <span className="text-xs font-medium">{tab.name}</span>
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500 text-center mt-3">
                {paymentTabs.find((t) => t.id === activeTab)?.description}
              </p>
            </div>

            {/* Content */}
            <div className="p-6 max-h-[400px] overflow-y-auto">
              {/* Amount Input */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Withdrawal Amount
                </label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 font-medium">
                    ₹
                  </span>
                  <input
                    type="number"
                    placeholder="0"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    className="w-full pl-8 pr-4 py-3 text-2xl font-bold text-gray-900 bg-gray-50 border border-gray-200 rounded-xl focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 transition-all"
                  />
                </div>
                <div className="flex justify-between mt-2">
                  <span className="text-xs text-gray-500">Minimum: ₹100</span>
                  <button
                    onClick={() => setAmount(balance.toString())}
                    className="text-xs text-emerald-600 font-medium hover:text-emerald-700"
                  >
                    Withdraw All
                  </button>
                </div>
              </div>

              {/* Payment Method Fields */}
              {renderPaymentFields()}

              {/* Error Message */}
              {error && (
                <div className="mt-4 flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-xl">
                  <AlertCircle size={16} className="text-red-500 flex-shrink-0" />
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-6 border-t border-gray-100 bg-gray-50">
              <Button
                onClick={handleWithdraw}
                disabled={loading}
                className="w-full py-3 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 shadow-lg shadow-emerald-500/30"
              >
                {loading ? (
                  <Loader2 size={20} className="animate-spin" />
                ) : (
                  <>
                    <ArrowDownToLine size={18} />
                    <span className="ml-2">Withdraw {amount ? formatCurrency(parseFloat(amount)) : ''}</span>
                  </>
                )}
              </Button>
              <p className="text-xs text-gray-500 text-center mt-3">
                By withdrawing, you agree to our terms and conditions.
                Processing fees may apply.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default WithdrawalModal;
