'use client';

import { useState } from 'react';
import {
  AlertTriangle,
  AlertCircle,
  Info,
  X,
  Scale,
  MapPin,
  DollarSign,
  Shield,
  Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Warning, WarningSeverity, WarningCategory } from '@/lib/types';

// ============================================================================
// Types
// ============================================================================

interface WarningBannerProps {
  warning: Warning;
  onDismiss?: () => void;
  dismissible?: boolean;
}

interface WarningListProps {
  warnings: Warning[];
  onDismiss?: (index: number) => void;
  dismissible?: boolean;
  maxVisible?: number;
}

// ============================================================================
// Helpers
// ============================================================================

const severityConfig: Record<
  WarningSeverity,
  {
    icon: typeof AlertTriangle;
    bgColor: string;
    borderColor: string;
    textColor: string;
    iconColor: string;
  }
> = {
  low: {
    icon: Info,
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    textColor: 'text-blue-900',
    iconColor: 'text-blue-600',
  },
  medium: {
    icon: AlertCircle,
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    textColor: 'text-yellow-900',
    iconColor: 'text-yellow-600',
  },
  high: {
    icon: AlertTriangle,
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
    textColor: 'text-orange-900',
    iconColor: 'text-orange-600',
  },
  critical: {
    icon: AlertTriangle,
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    textColor: 'text-red-900',
    iconColor: 'text-red-600',
  },
};

const categoryIcons: Record<WarningCategory, typeof Scale> = {
  legal: Scale,
  brand: Sparkles,
  location: MapPin,
  budget: DollarSign,
  risk: Shield,
};

// ============================================================================
// Component
// ============================================================================

export function WarningBanner({
  warning,
  onDismiss,
  dismissible = true,
}: WarningBannerProps) {
  const [isDismissed, setIsDismissed] = useState(false);

  if (isDismissed) return null;

  const config = severityConfig[warning.severity];
  const Icon = config.icon;
  const CategoryIcon = categoryIcons[warning.category];

  const handleDismiss = () => {
    setIsDismissed(true);
    onDismiss?.();
  };

  return (
    <div
      className={cn(
        'rounded-lg border p-4',
        config.bgColor,
        config.borderColor
      )}
      role="alert"
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className="flex-shrink-0">
          <Icon className={cn('h-5 w-5', config.iconColor)} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <CategoryIcon className={cn('h-4 w-4', config.iconColor)} />
            <span
              className={cn(
                'text-xs font-medium uppercase tracking-wide',
                config.textColor
              )}
            >
              {warning.category}
            </span>
            <span
              className={cn(
                'text-xs px-2 py-0.5 rounded-full',
                config.bgColor,
                config.textColor
              )}
            >
              {warning.severity}
            </span>
          </div>

          <p className={cn('text-sm font-medium', config.textColor)}>
            {warning.message}
          </p>

          {warning.affectedItems.length > 0 && (
            <div className="mt-2">
              <p className={cn('text-xs', config.textColor, 'opacity-75')}>
                Affected items:
              </p>
              <ul className="mt-1 space-y-1">
                {warning.affectedItems.map((item, index) => (
                  <li
                    key={index}
                    className={cn('text-xs', config.textColor, 'opacity-90')}
                  >
                    • {item}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Dismiss Button */}
        {dismissible && (
          <button
            onClick={handleDismiss}
            className={cn(
              'flex-shrink-0 p-1 rounded hover:bg-black/5 transition-colors',
              config.textColor
            )}
            aria-label="Dismiss warning"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// Warning List
// ============================================================================

export function WarningList({
  warnings,
  onDismiss,
  dismissible = true,
  maxVisible = 5,
}: WarningListProps) {
  const [dismissedIndices, setDismissedIndices] = useState<Set<number>>(
    new Set()
  );

  const visibleWarnings = warnings.filter(
    (_, index) => !dismissedIndices.has(index)
  );

  const displayedWarnings = visibleWarnings.slice(0, maxVisible);
  const remainingCount = visibleWarnings.length - maxVisible;

  const handleDismiss = (index: number) => {
    setDismissedIndices((prev) => new Set(prev).add(index));
    onDismiss?.(index);
  };

  if (visibleWarnings.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      {displayedWarnings.map((warning, displayIndex) => {
        const originalIndex = warnings.indexOf(warning);
        return (
          <WarningBanner
            key={originalIndex}
            warning={warning}
            onDismiss={() => handleDismiss(originalIndex)}
            dismissible={dismissible}
          />
        );
      })}

      {remainingCount > 0 && (
        <div className="text-sm text-gray-600 text-center py-2">
          +{remainingCount} more warning{remainingCount !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Compact Warning Badge
// ============================================================================

export function WarningBadge({ warning }: { warning: Warning }) {
  const config = severityConfig[warning.severity];
  const Icon = config.icon;

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium',
        config.bgColor,
        config.textColor
      )}
    >
      <Icon className="h-3 w-3" />
      <span className="capitalize">{warning.severity}</span>
    </div>
  );
}
