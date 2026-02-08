'use client';

import { Check, Lock } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { StepperProps } from '@/lib/types';

const WORKFLOW_STEPS = [
  { id: 'brief', label: 'Brief' },
  { id: 'concept', label: 'Concept' },
  { id: 'screenplays', label: 'Screenplays' },
  { id: 'select', label: 'Select' },
  { id: 'storyboard', label: 'Storyboard' },
  { id: 'production', label: 'Production' },
  { id: 'export', label: 'Export' },
] as const;

export function Stepper({
  currentStep,
  completedSteps,
  lockedSteps,
  onStepClick,
}: StepperProps) {
  const currentIndex = WORKFLOW_STEPS.findIndex((s) => s.id === currentStep);

  return (
    <nav aria-label="Progress" className="py-4">
      <ol className="space-y-2">
        {WORKFLOW_STEPS.map((step, index) => {
          const isCompleted = completedSteps.includes(step.id);
          const isCurrent = step.id === currentStep;
          const isLocked = lockedSteps.includes(step.id);
          const isPast = index < currentIndex;

          return (
            <li key={step.id}>
              <button
                onClick={() => !isLocked && onStepClick(step.id)}
                disabled={isLocked}
                className={cn(
                  'w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all',
                  'text-left',
                  isCurrent && 'bg-blue-50 border-2 border-blue-500',
                  !isCurrent && !isLocked && 'hover:bg-gray-50',
                  isLocked && 'opacity-50 cursor-not-allowed'
                )}
              >
                {/* Step Icon */}
                <div
                  className={cn(
                    'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
                    'transition-colors',
                    isCompleted && 'bg-green-500 text-white',
                    isCurrent && !isCompleted && 'bg-blue-500 text-white',
                    !isCurrent && !isCompleted && !isLocked && 'bg-gray-200 text-gray-600',
                    isLocked && 'bg-gray-100 text-gray-400'
                  )}
                >
                  {isCompleted ? (
                    <Check className="h-5 w-5" />
                  ) : isLocked ? (
                    <Lock className="h-4 w-4" />
                  ) : (
                    <span className="text-sm font-medium">{index + 1}</span>
                  )}
                </div>

                {/* Step Label */}
                <div className="flex-1 min-w-0">
                  <p
                    className={cn(
                      'text-sm font-medium',
                      isCurrent && 'text-blue-900',
                      !isCurrent && !isLocked && 'text-gray-900',
                      isLocked && 'text-gray-400'
                    )}
                  >
                    {step.label}
                  </p>
                  {isCurrent && (
                    <p className="text-xs text-blue-600 mt-0.5">Current step</p>
                  )}
                  {isLocked && (
                    <p className="text-xs text-gray-400 mt-0.5">Locked</p>
                  )}
                </div>

                {/* Connector Line */}
                {index < WORKFLOW_STEPS.length - 1 && (
                  <div
                    className={cn(
                      'absolute left-8 top-full h-2 w-0.5 -translate-x-1/2',
                      isPast || isCompleted ? 'bg-green-500' : 'bg-gray-200'
                    )}
                    style={{ marginTop: '-0.5rem' }}
                  />
                )}
              </button>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
