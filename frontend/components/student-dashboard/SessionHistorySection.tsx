/**
 * Session History Section Component for Student Dashboard
 *
 * Displays past sessions with:
 * - Completed, cancelled, no-show status
 * - Instructor info and subject
 * - Date and duration
 * - Review option for completed sessions
 * - Instructor notes (if any)
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  History,
  CheckCircle,
  XCircle,
  AlertCircle,
  Star,
  User,
  Calendar,
  Clock,
  ChevronRight,
  MessageSquare,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { Card, Button, Badge } from '../UIComponents';
import { SessionHistory } from '../../services/studentAPI';

interface SessionHistorySectionProps {
  sessions: SessionHistory[];
  onReview?: (sessionId: number) => void;
}

interface SessionHistoryItemProps {
  session: SessionHistory;
  index: number;
  onReview?: (sessionId: number) => void;
}

const SessionHistoryItem: React.FC<SessionHistoryItemProps> = ({
  session,
  index,
  onReview,
}) => {
  const [showNotes, setShowNotes] = useState(false);

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
      case 'cancelled':
        return {
          icon: XCircle,
          color: 'text-red-500',
          bg: 'bg-red-100',
          label: 'Cancelled',
          badgeVariant: 'neutral' as const,
        };
      case 'no_show':
        return {
          icon: AlertCircle,
          color: 'text-amber-500',
          bg: 'bg-amber-100',
          label: 'No Show',
          badgeVariant: 'secondary' as const,
        };
      default:
        return {
          icon: History,
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
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
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

  const statusConfig = getStatusConfig(session.status);
  const StatusIcon = statusConfig.icon;

  return (
    <div
      className="group relative bg-white/60 backdrop-blur-sm rounded-xl border border-white/50 p-4 transition-all duration-300 hover:bg-white/80"
      style={{
        animation: `fadeIn 0.4s ease-out forwards`,
        animationDelay: `${index * 0.08}s`,
        opacity: 0,
      }}
    >
      <div className="flex items-start gap-4">
        {/* Instructor Photo */}
        <div className="relative flex-shrink-0">
          {session.instructor_photo_url ? (
            <img
              src={session.instructor_photo_url}
              alt={session.instructor_name}
              className="w-12 h-12 rounded-xl object-cover border-2 border-white shadow-sm"
            />
          ) : (
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-gray-100 to-gray-50 flex items-center justify-center shadow-sm">
              <User size={20} className="text-gray-400" />
            </div>
          )}
          {/* Status indicator */}
          <div
            className={`absolute -bottom-1 -right-1 w-5 h-5 rounded-full ${statusConfig.bg} flex items-center justify-center`}
          >
            <StatusIcon size={12} className={statusConfig.color} />
          </div>
        </div>

        {/* Session Info */}
        <div className="flex-grow min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-semibold text-gray-900 truncate">
              {session.instructor_name}
            </h4>
            <Badge variant={statusConfig.badgeVariant}>
              {statusConfig.label}
            </Badge>
          </div>

          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <Calendar size={12} />
              {formatDate(session.start_at)}
            </span>
            <span className="flex items-center gap-1">
              <Clock size={12} />
              {formatTime(session.start_at)}
            </span>
            <span className="text-xs text-gray-400">
              {session.duration_minutes}min
            </span>
          </div>

          {session.subject && (
            <span className="inline-block mt-2 text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
              {session.subject}
            </span>
          )}

          {/* Instructor Notes */}
          {session.instructor_notes && (
            <div className="mt-3">
              <button
                onClick={() => setShowNotes(!showNotes)}
                className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700 transition-colors"
              >
                <MessageSquare size={12} />
                Instructor Notes
                {showNotes ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>
              {showNotes && (
                <div className="mt-2 p-3 bg-gray-50 rounded-lg text-sm text-gray-600 border border-gray-100">
                  {session.instructor_notes}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Side - Price & Review */}
        <div className="flex flex-col items-end gap-2 flex-shrink-0">
          <span className="text-sm font-semibold text-gray-900">
            {formatCurrency(session.amount, session.currency)}
          </span>

          {session.status === 'completed' && (
            <>
              {session.has_review ? (
                <div className="flex items-center gap-1 text-amber-500">
                  <Star size={14} className="fill-amber-500" />
                  <span className="text-xs font-medium">Reviewed</span>
                </div>
              ) : session.can_review ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onReview?.(session.session_id)}
                  className="gap-1 text-xs"
                >
                  <Star size={12} />
                  Review
                </Button>
              ) : null}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export const SessionHistorySection: React.FC<SessionHistorySectionProps> = ({
  sessions,
  onReview,
}) => {
  // Calculate summary stats
  const completedCount = sessions.filter((s) => s.status === 'completed').length;
  const cancelledCount = sessions.filter((s) => s.status === 'cancelled').length;

  if (sessions.length === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
            <History size={18} className="text-purple-600" />
          </div>
          Session History
        </h3>
        <div className="bg-gradient-to-br from-gray-50 to-white rounded-xl p-8 text-center border-2 border-dashed border-gray-200/80">
          <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-inner">
            <History size={28} className="text-gray-400" />
          </div>
          <h4 className="font-semibold text-gray-700 mb-1">No sessions yet</h4>
          <p className="text-gray-400 text-sm max-w-xs mx-auto">
            Your past sessions will appear here after completion
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
            <History size={18} className="text-purple-600" />
          </div>
          Session History
        </h3>
        <Link
          to="/my-sessions/history"
          className="flex items-center gap-1 text-primary-600 text-sm font-medium hover:text-primary-700 transition-colors group"
        >
          View All
          <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
        </Link>
      </div>

      {/* Summary stats */}
      <div className="flex items-center gap-4 mb-4 text-sm">
        <span className="flex items-center gap-1.5 text-green-600">
          <CheckCircle size={14} />
          <span className="font-medium">{completedCount}</span> completed
        </span>
        {cancelledCount > 0 && (
          <span className="flex items-center gap-1.5 text-gray-500">
            <XCircle size={14} />
            <span className="font-medium">{cancelledCount}</span> cancelled
          </span>
        )}
      </div>

      <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
        {sessions.slice(0, 10).map((session, index) => (
          <SessionHistoryItem
            key={session.session_id}
            session={session}
            index={index}
            onReview={onReview}
          />
        ))}
      </div>

      {sessions.length > 10 && (
        <div className="mt-4 pt-4 border-t border-gray-100 text-center">
          <Link
            to="/my-sessions/history"
            className="text-sm text-gray-500 hover:text-primary-600 transition-colors"
          >
            View all {sessions.length} sessions
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

export default SessionHistorySection;
