/**
 * Payment History Section Component for Student Dashboard
 *
 * Displays payment transactions with:
 * - Payment status (completed, refunded, failed, pending, processing)
 * - Instructor name and lesson type
 * - Amount and date
 * - Refund status if applicable
 * - Link to session details
 */

import React from 'react';
import { Link } from 'react-router-dom';
import {
  CreditCard,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw,
  AlertTriangle,
  ChevronRight,
  Download,
  Calendar,
  Sparkles,
} from 'lucide-react';
import { Card, Button, Badge } from '../UIComponents';
import { PaymentHistory } from '../../services/studentAPI';

interface PaymentHistorySectionProps {
  payments: PaymentHistory[];
}

interface PaymentItemProps {
  payment: PaymentHistory;
  index: number;
}

const PaymentItem: React.FC<PaymentItemProps> = ({ payment, index }) => {
  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'completed':
        return {
          icon: CheckCircle,
          color: 'text-green-600',
          bg: 'bg-green-100',
          label: 'Completed',
          badgeVariant: 'primary' as const,
        };
      case 'refunded':
        return {
          icon: RefreshCw,
          color: 'text-blue-500',
          bg: 'bg-blue-100',
          label: 'Refunded',
          badgeVariant: 'secondary' as const,
        };
      case 'failed':
        return {
          icon: XCircle,
          color: 'text-red-500',
          bg: 'bg-red-100',
          label: 'Failed',
          badgeVariant: 'neutral' as const,
        };
      case 'pending':
        return {
          icon: Clock,
          color: 'text-amber-500',
          bg: 'bg-amber-100',
          label: 'Pending',
          badgeVariant: 'secondary' as const,
        };
      case 'processing':
        return {
          icon: RefreshCw,
          color: 'text-blue-500',
          bg: 'bg-blue-100',
          label: 'Processing',
          badgeVariant: 'secondary' as const,
        };
      default:
        return {
          icon: CreditCard,
          color: 'text-gray-500',
          bg: 'bg-gray-100',
          label: status,
          badgeVariant: 'neutral' as const,
        };
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const statusConfig = getStatusConfig(payment.status);
  const StatusIcon = statusConfig.icon;

  return (
    <div
      className="group flex items-center gap-4 p-4 bg-white/60 backdrop-blur-sm rounded-xl border border-white/50 transition-all duration-300 hover:bg-white/80"
      style={{
        animation: `fadeIn 0.4s ease-out forwards`,
        animationDelay: `${index * 0.08}s`,
        opacity: 0,
      }}
    >
      {/* Status Icon */}
      <div
        className={`w-10 h-10 rounded-xl ${statusConfig.bg} flex items-center justify-center flex-shrink-0`}
      >
        <StatusIcon
          size={18}
          className={`${statusConfig.color} ${payment.status === 'processing' ? 'animate-spin' : ''}`}
        />
      </div>

      {/* Payment Info */}
      <div className="flex-grow min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h4 className="font-semibold text-gray-900 truncate">
            {payment.instructor_name}
          </h4>
          {payment.lesson_type === 'trial' && (
            <Badge variant="secondary">
              <Sparkles size={10} className="mr-1" />
              Trial
            </Badge>
          )}
        </div>

        <div className="flex items-center gap-3 text-sm text-gray-500">
          <span className="flex items-center gap-1">
            <Calendar size={12} />
            {formatDate(payment.created_at)}
          </span>
          {payment.payment_method && (
            <span className="flex items-center gap-1">
              <CreditCard size={12} />
              {payment.payment_method}
            </span>
          )}
        </div>

        {/* Refund status */}
        {payment.refund_status && (
          <div className="mt-1">
            <span className="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
              Refund: {payment.refund_status}
            </span>
          </div>
        )}
      </div>

      {/* Amount & Status */}
      <div className="flex flex-col items-end gap-1 flex-shrink-0">
        <span
          className={`text-lg font-bold ${
            payment.status === 'refunded'
              ? 'text-blue-600'
              : payment.status === 'failed'
                ? 'text-red-500 line-through'
                : 'text-gray-900'
          }`}
        >
          {payment.status === 'refunded' && '-'}
          {formatCurrency(payment.amount, payment.currency)}
        </span>
        <Badge variant={statusConfig.badgeVariant}>{statusConfig.label}</Badge>
      </div>

      {/* Link to session if available */}
      {payment.session_id && (
        <Link
          to={`/my-sessions/${payment.session_id}`}
          className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
          title="View session"
        >
          <ChevronRight size={16} />
        </Link>
      )}
    </div>
  );
};

export const PaymentHistorySection: React.FC<PaymentHistorySectionProps> = ({
  payments,
}) => {
  // Calculate total spent
  const totalSpent = payments
    .filter((p) => p.status === 'completed')
    .reduce((sum, p) => sum + p.amount, 0);

  const totalRefunded = payments
    .filter((p) => p.status === 'refunded')
    .reduce((sum, p) => sum + p.amount, 0);

  const currency = payments[0]?.currency || 'INR';

  const formatCurrency = (amount: number, curr: string) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: curr,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (payments.length === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <div className="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center">
            <CreditCard size={18} className="text-emerald-600" />
          </div>
          Payment History
        </h3>
        <div className="bg-gradient-to-br from-gray-50 to-white rounded-xl p-8 text-center border-2 border-dashed border-gray-200/80">
          <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-inner">
            <CreditCard size={28} className="text-gray-400" />
          </div>
          <h4 className="font-semibold text-gray-700 mb-1">No payments yet</h4>
          <p className="text-gray-400 text-sm max-w-xs mx-auto">
            Your payment history will appear here after your first transaction
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <div className="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center">
            <CreditCard size={18} className="text-emerald-600" />
          </div>
          Payment History
        </h3>
        <Link
          to="/my-payments"
          className="flex items-center gap-1 text-primary-600 text-sm font-medium hover:text-primary-700 transition-colors group"
        >
          View All
          <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
        </Link>
      </div>

      {/* Summary stats */}
      <div className="flex items-center gap-6 mb-4 p-3 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100">
        <div>
          <span className="text-xs text-gray-500 block">Total Spent</span>
          <span className="text-lg font-bold text-gray-900">
            {formatCurrency(totalSpent, currency)}
          </span>
        </div>
        {totalRefunded > 0 && (
          <div className="pl-6 border-l border-gray-200">
            <span className="text-xs text-gray-500 block">Refunded</span>
            <span className="text-lg font-bold text-blue-600">
              {formatCurrency(totalRefunded, currency)}
            </span>
          </div>
        )}
        <div className="ml-auto">
          <span className="text-xs text-gray-500 block">Transactions</span>
          <span className="text-lg font-bold text-gray-900">{payments.length}</span>
        </div>
      </div>

      <div className="space-y-3 max-h-[350px] overflow-y-auto pr-2">
        {payments.slice(0, 8).map((payment, index) => (
          <PaymentItem key={payment.payment_id} payment={payment} index={index} />
        ))}
      </div>

      {payments.length > 8 && (
        <div className="mt-4 pt-4 border-t border-gray-100 text-center">
          <Link
            to="/my-payments"
            className="text-sm text-gray-500 hover:text-primary-600 transition-colors"
          >
            View all {payments.length} transactions
          </Link>
        </div>
      )}

      {/* CSS animations */}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </Card>
  );
};

export default PaymentHistorySection;
