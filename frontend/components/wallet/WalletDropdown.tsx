/**
 * Wallet Dropdown Component
 * Shows wallet balance with dropdown for withdrawal options
 */

import React, { useState, useEffect } from 'react';
import { Wallet, ChevronDown, ArrowDownToLine, History, TrendingUp } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/axios';
import WithdrawalModal from './WithdrawalModal';

interface WalletBalance {
  wallet_id: number;
  instructor_id: number;
  balance: number;
  total_earned: number;
  total_withdrawn: number;
  currency: string;
  status: string;
  can_withdraw: boolean;
}

const WalletDropdown: React.FC = () => {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [walletData, setWalletData] = useState<WalletBalance | null>(null);
  const [loading, setLoading] = useState(true);
  const [showWithdrawalModal, setShowWithdrawalModal] = useState(false);

  // Only show for instructors
  if (user?.role !== 'instructor') {
    return null;
  }

  useEffect(() => {
    fetchWalletBalance();
  }, []);

  const fetchWalletBalance = async () => {
    try {
      setLoading(true);
      const response = await api.get('/wallet/balance');
      setWalletData(response.data);
    } catch (error: any) {
      // If wallet doesn't exist yet, show 0 balance
      if (error.response?.status === 404) {
        setWalletData({
          wallet_id: 0,
          instructor_id: 0,
          balance: 0,
          total_earned: 0,
          total_withdrawn: 0,
          currency: 'INR',
          status: 'active',
          can_withdraw: false,
        });
      }
      console.error('Error fetching wallet:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <>
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          className={`
            flex items-center gap-2 px-3 py-2 rounded-xl
            transition-all duration-300
            ${isOpen
              ? 'bg-gradient-to-r from-emerald-50 to-green-50 shadow-lg border border-emerald-200'
              : 'hover:bg-white/50 border border-transparent'
            }
          `}
        >
          {/* Wallet Icon */}
          <div
            className={`
              relative p-2 rounded-lg
              bg-gradient-to-br from-emerald-500 to-green-600
              transition-all duration-300
              ${isHovered ? 'scale-110 shadow-lg shadow-emerald-500/30' : ''}
            `}
          >
            <Wallet size={16} className="text-white" />
          </div>

          {/* Balance */}
          <div className="text-left">
            <span className="text-sm font-bold text-gray-900">
              {loading ? '...' : formatCurrency(walletData?.balance || 0)}
            </span>
          </div>

          <ChevronDown
            size={16}
            className={`
              text-gray-400 transition-transform duration-300
              ${isOpen ? 'rotate-180' : ''}
            `}
          />
        </button>

        {/* Dropdown Menu */}
        {isOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 z-40"
              onClick={() => setIsOpen(false)}
            />

            {/* Menu */}
            <div
              className="absolute right-0 top-full mt-2 w-72 z-50
                bg-white/95 backdrop-blur-xl rounded-2xl
                border border-white/50 shadow-2xl shadow-gray-200/50
                overflow-hidden animate-slideDown"
            >
              {/* Balance Header */}
              <div className="p-4 bg-gradient-to-r from-emerald-50 to-green-50 border-b border-emerald-100">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-gray-600">Available Balance</span>
                  <span className={`
                    text-xs px-2 py-0.5 rounded-full font-medium
                    ${walletData?.status === 'active'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-600'
                    }
                  `}>
                    {walletData?.status || 'Active'}
                  </span>
                </div>
                <div className="text-3xl font-extrabold text-gray-900">
                  {loading ? '...' : formatCurrency(walletData?.balance || 0)}
                </div>
              </div>

              {/* Stats */}
              <div className="p-4 grid grid-cols-2 gap-3 border-b border-gray-100">
                <div className="bg-gray-50 rounded-xl p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <TrendingUp size={14} className="text-emerald-500" />
                    <span className="text-xs text-gray-500">Total Earned</span>
                  </div>
                  <span className="text-sm font-bold text-gray-900">
                    {loading ? '...' : formatCurrency(walletData?.total_earned || 0)}
                  </span>
                </div>
                <div className="bg-gray-50 rounded-xl p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <ArrowDownToLine size={14} className="text-blue-500" />
                    <span className="text-xs text-gray-500">Withdrawn</span>
                  </div>
                  <span className="text-sm font-bold text-gray-900">
                    {loading ? '...' : formatCurrency(walletData?.total_withdrawn || 0)}
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="p-3 space-y-2">
                <button
                  onClick={() => {
                    setIsOpen(false);
                    setShowWithdrawalModal(true);
                  }}
                  disabled={!walletData?.can_withdraw || (walletData?.balance || 0) <= 0}
                  className={`
                    w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl
                    font-semibold text-sm transition-all duration-300
                    ${walletData?.can_withdraw && (walletData?.balance || 0) > 0
                      ? 'bg-gradient-to-r from-emerald-500 to-green-600 text-white shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:scale-[1.02]'
                      : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    }
                  `}
                >
                  <ArrowDownToLine size={18} />
                  Withdraw Money
                </button>

                <button
                  onClick={() => {
                    setIsOpen(false);
                    // TODO: Navigate to transaction history
                  }}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl
                    font-medium text-sm text-gray-600 hover:bg-gray-50 transition-colors"
                >
                  <History size={16} />
                  Transaction History
                </button>
              </div>

              {/* Info */}
              {!walletData?.can_withdraw && (
                <div className="px-4 pb-4">
                  <p className="text-xs text-gray-500 text-center">
                    Complete your profile verification to enable withdrawals
                  </p>
                </div>
              )}
            </div>
          </>
        )}
      </div>

      {/* Withdrawal Modal */}
      <WithdrawalModal
        isOpen={showWithdrawalModal}
        onClose={() => setShowWithdrawalModal(false)}
        balance={walletData?.balance || 0}
        onSuccess={() => {
          fetchWalletBalance();
          setShowWithdrawalModal(false);
        }}
      />
    </>
  );
};

export default WalletDropdown;
