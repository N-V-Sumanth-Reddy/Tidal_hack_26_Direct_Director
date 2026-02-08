'use client';

import { Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Concept } from '@/lib/types';
import { MarkdownRenderer } from '@/components/shared/MarkdownRenderer';

interface ConceptStepProps {
  concept?: Concept;
  onGenerateScreenplays: () => void;
  isGenerating?: boolean;
}

export function ConceptStep({
  concept,
  onGenerateScreenplays,
  isGenerating,
}: ConceptStepProps) {
  // Show concept if available
  if (concept) {
    return (
      <div className="max-w-3xl space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Creative Concept</h2>
          <p className="text-sm text-gray-500">
            Generated on {new Date(concept.generatedAt).toLocaleString()}
          </p>
        </div>

        {/* Title */}
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-start gap-3 mb-4">
            <Sparkles className="h-6 w-6 text-blue-500 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-xl font-semibold text-gray-900">{concept.title}</h3>
              {concept.version && (
                <span className="text-sm text-gray-500">Version {concept.version}</span>
              )}
            </div>
          </div>

          {/* Description - Rendered as Markdown */}
          <div className="space-y-4">
            <div>
              <MarkdownRenderer content={concept.description} />
            </div>
          </div>
        </div>

        {/* Generate Screenplays Button */}
        <div className="flex justify-end pt-6 border-t">
          <button
            onClick={onGenerateScreenplays}
            disabled={isGenerating}
            className={cn(
              'flex items-center gap-2 px-6 py-3 rounded-lg',
              'bg-blue-500 text-white font-medium',
              'hover:bg-blue-600 transition-colors',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            {isGenerating ? (
              <>
                <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="h-5 w-5" />
                Generate Screenplays
              </>
            )}
          </button>
        </div>
      </div>
    );
  }

  // No concept yet
  return (
    <div className="max-w-3xl">
      <div className="bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
        <Sparkles className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Concept Yet</h3>
        <p className="text-gray-600">
          Submit a brief to generate a creative concept for your ad campaign.
        </p>
      </div>
    </div>
  );
}
