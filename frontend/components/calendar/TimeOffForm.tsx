/**
 * Time Off Form Component
 * Form for adding time off periods
 */

import React, { useState } from 'react';
import { CalendarOff, Plus, X } from 'lucide-react';

interface TimeOffFormProps {
  onSubmit: (data: {
    start_at: string;
    end_at: string;
    reason?: string;
  }) => Promise<void>;
  isLoading?: boolean;
}

export const TimeOffForm: React.FC<TimeOffFormProps> = ({
  onSubmit,
  isLoading = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [startTime, setStartTime] = useState('09:00');
  const [endDate, setEndDate] = useState('');
  const [endTime, setEndTime] = useState('17:00');
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!startDate || !endDate) {
      setError('Please select both start and end dates');
      return;
    }

    const startDateTime = `${startDate}T${startTime}:00`;
    const endDateTime = `${endDate}T${endTime}:00`;

    if (new Date(startDateTime) >= new Date(endDateTime)) {
      setError('End time must be after start time');
      return;
    }

    try {
      await onSubmit({
        start_at: startDateTime,
        end_at: endDateTime,
        reason: reason || undefined,
      });
      // Reset and close
      setIsOpen(false);
      resetForm();
    } catch (err: any) {
      setError(err.message || 'Failed to add time off');
    }
  };

  const resetForm = () => {
    setStartDate('');
    setStartTime('09:00');
    setEndDate('');
    setEndTime('17:00');
    setReason('');
    setError('');
  };

  // Quick actions for common time off patterns
  const setAllDay = () => {
    setStartTime('00:00');
    setEndTime('23:59');
  };

  const setTomorrow = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateStr = tomorrow.toISOString().split('T')[0];
    setStartDate(dateStr);
    setEndDate(dateStr);
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium"
      >
        <CalendarOff className="h-5 w-5" />
        Add Time Off
      </button>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <CalendarOff className="h-5 w-5 text-gray-600" />
          Add Time Off
        </h3>
        <button
          onClick={() => {
            setIsOpen(false);
            resetForm();
          }}
          className="p-1 hover:bg-gray-100 rounded-full"
        >
          <X className="h-5 w-5 text-gray-400" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Quick Actions */}
        <div className="flex gap-2">
          <button
            type="button"
            onClick={setTomorrow}
            className="px-3 py-1.5 text-xs bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Tomorrow
          </button>
          <button
            type="button"
            onClick={setAllDay}
            className="px-3 py-1.5 text-xs bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            All Day
          </button>
        </div>

        {/* Start Date/Time */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Start
          </label>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="time"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* End Date/Time */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            End
          </label>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              min={startDate || new Date().toISOString().split('T')[0]}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="time"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Reason */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Reason (optional)
          </label>
          <input
            type="text"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="e.g., Vacation, Personal, Holiday"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            maxLength={500}
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => {
              setIsOpen(false);
              resetForm();
            }}
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Adding...' : 'Add Time Off'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default TimeOffForm;
