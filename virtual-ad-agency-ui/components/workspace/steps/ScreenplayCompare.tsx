'use client';

import { Check, Clock, DollarSign, Target, ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Screenplay } from '@/lib/types';
import { MarkdownRenderer } from '@/components/shared/MarkdownRenderer';
import { useState } from 'react';

interface ScreenplayCompareProps {
  screenplays: [Screenplay, Screenplay];
  selectedId?: string;
  onSelect: (screenplayId: string) => void;
  isSelecting?: boolean;
}

export function ScreenplayCompare({
  screenplays,
  selectedId,
  onSelect,
  isSelecting,
}: ScreenplayCompareProps) {
  const [screenplayA, screenplayB] = screenplays;
  const [expandedA, setExpandedA] = useState(false);
  const [expandedB, setExpandedB] = useState(false);

  const renderScreenplay = (screenplay: Screenplay, isSelected: boolean, isExpanded: boolean, setExpanded: (val: boolean) => void) => (
    <div
      className={cn(
        'flex-1 rounded-lg border-2 p-6 transition-all',
        isSelected
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-200 bg-white hover:border-gray-300'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">
            Variant {screenplay.variant}
          </h3>
          <p className="text-sm text-gray-500">
            {screenplay.scenes.length} scenes • {screenplay.totalDuration}s
          </p>
        </div>
        {isSelected && (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500 text-white text-sm font-medium">
            <Check className="h-4 w-4" />
            Selected
          </div>
        )}
      </div>

      {/* Scores */}
      {screenplay.scores && (
        <div className="grid grid-cols-3 gap-3 mb-6">
          <div className="bg-white rounded-lg p-3 border">
            <div className="flex items-center gap-2 mb-1">
              <Target className="h-4 w-4 text-blue-500" />
              <span className="text-xs font-medium text-gray-600">Clarity</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {screenplay.scores.clarity.toFixed(1)}
            </p>
          </div>
          <div className="bg-white rounded-lg p-3 border">
            <div className="flex items-center gap-2 mb-1">
              <Clock className="h-4 w-4 text-green-500" />
              <span className="text-xs font-medium text-gray-600">Feasibility</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {screenplay.scores.feasibility.toFixed(1)}
            </p>
          </div>
          <div className="bg-white rounded-lg p-3 border">
            <div className="flex items-center gap-2 mb-1">
              <DollarSign className="h-4 w-4 text-yellow-500" />
              <span className="text-xs font-medium text-gray-600">Cost Risk</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {screenplay.scores.costRisk.toFixed(1)}
            </p>
          </div>
        </div>
      )}

      {/* Scenes */}
      <div className="space-y-3 mb-6">
        <h4 className="text-sm font-medium text-gray-700">Scenes</h4>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {screenplay.scenes.map((scene, index) => (
            <div key={index} className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-700 text-xs font-medium flex items-center justify-center">
                  {index + 1}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-gray-900 line-clamp-3">
                    <MarkdownRenderer content={scene.description} className="text-sm" />
                  </div>
                  {scene.duration && (
                    <p className="text-xs text-gray-500 mt-1">{scene.duration}s</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Full Screenplay (Expandable) */}
      {(screenplay as any).formattedText && (
        <div className="mb-6">
          <button
            onClick={() => setExpanded(!isExpanded)}
            className="flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="h-4 w-4" />
                Hide Full Screenplay
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4" />
                View Full Screenplay
              </>
            )}
          </button>
          
          {isExpanded && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200 max-h-[600px] overflow-y-auto">
              <MarkdownRenderer content={(screenplay as any).formattedText} />
            </div>
          )}
        </div>
      )}

      {/* Select Button */}
      <button
        onClick={() => onSelect(screenplay.id)}
        disabled={isSelecting || isSelected}
        className={cn(
          'w-full py-3 rounded-lg font-medium transition-colors',
          'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
          isSelected
            ? 'bg-blue-500 text-white cursor-default'
            : 'bg-gray-100 text-gray-900 hover:bg-gray-200',
          'disabled:opacity-50 disabled:cursor-not-allowed'
        )}
      >
        {isSelecting ? (
          <span className="flex items-center justify-center gap-2">
            <div className="h-5 w-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
            Selecting...
          </span>
        ) : isSelected ? (
          'Selected'
        ) : (
          'Choose This Screenplay'
        )}
      </button>
    </div>
  );

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Compare Screenplays</h2>
        <p className="text-gray-600">
          Review both screenplay variants and select the one that best fits your vision.
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {renderScreenplay(screenplayA, selectedId === screenplayA.id, expandedA, setExpandedA)}
        {renderScreenplay(screenplayB, selectedId === screenplayB.id, expandedB, setExpandedB)}
      </div>

      {selectedId && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-green-800 font-medium">
            ✓ Screenplay selected! You can now proceed to generate the storyboard.
          </p>
        </div>
      )}
    </div>
  );
}
