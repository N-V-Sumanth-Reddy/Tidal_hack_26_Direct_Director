import { X, DollarSign, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ProgressIndicatorProps } from '@/lib/types';

// ============================================================================
// Component
// ============================================================================

export function ProgressIndicator({ state, onCancel }: ProgressIndicatorProps) {
  const { progress, estimatedTime, estimatedCost, canCancel, error } = state;

  // Format time remaining
  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${minutes}m ${secs}s`;
  };

  // Format cost
  const formatCost = (cost: number): string => {
    return `$${cost.toFixed(2)}`;
  };

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <div className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center">
              <X className="h-5 w-5 text-red-600" />
            </div>
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-medium text-red-900">
              Generation Failed
            </h3>
            <p className="mt-1 text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-white p-6 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Generating...</h3>
        {canCancel && (
          <button
            onClick={onCancel}
            className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            {Math.round(progress)}%
          </span>
          <span className="text-xs text-gray-500">
            {progress < 100 ? 'In progress' : 'Complete'}
          </span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={cn(
              'h-full transition-all duration-500 ease-out',
              progress < 100
                ? 'bg-blue-600'
                : 'bg-green-600'
            )}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Estimates */}
      <div className="grid grid-cols-2 gap-4">
        {/* Time Remaining */}
        {estimatedTime > 0 && progress < 100 && (
          <div className="flex items-center gap-2 text-sm">
            <Clock className="h-4 w-4 text-gray-400" />
            <div>
              <div className="text-gray-500">Time remaining</div>
              <div className="font-medium text-gray-900">
                {formatTime(estimatedTime)}
              </div>
            </div>
          </div>
        )}

        {/* Estimated Cost */}
        {estimatedCost > 0 && (
          <div className="flex items-center gap-2 text-sm">
            <DollarSign className="h-4 w-4 text-gray-400" />
            <div>
              <div className="text-gray-500">Estimated cost</div>
              <div className="font-medium text-gray-900">
                {formatCost(estimatedCost)}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Loading Animation */}
      {progress < 100 && (
        <div className="mt-4 flex items-center gap-2 text-sm text-gray-500">
          <div className="flex gap-1">
            <div className="h-2 w-2 rounded-full bg-blue-600 animate-bounce [animation-delay:-0.3s]" />
            <div className="h-2 w-2 rounded-full bg-blue-600 animate-bounce [animation-delay:-0.15s]" />
            <div className="h-2 w-2 rounded-full bg-blue-600 animate-bounce" />
          </div>
          <span>Processing your request...</span>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Compact Variant
// ============================================================================

export function CompactProgressIndicator({
  state,
  onCancel,
}: ProgressIndicatorProps) {
  const { progress, canCancel } = state;

  return (
    <div className="flex items-center gap-3">
      <div className="flex-1">
        <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-600 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
      <span className="text-sm font-medium text-gray-700 min-w-[3rem]">
        {Math.round(progress)}%
      </span>
      {canCancel && (
        <button
          onClick={onCancel}
          className="text-gray-400 hover:text-gray-600 transition-colors"
          aria-label="Cancel generation"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
