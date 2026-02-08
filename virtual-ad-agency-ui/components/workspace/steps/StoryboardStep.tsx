'use client';

import type { Storyboard } from '@/lib/types';
import { MarkdownRenderer } from '@/components/shared/MarkdownRenderer';

interface StoryboardStepProps {
  storyboard?: Storyboard;
  onGenerateStoryboard?: () => void;
  onGenerateProduction?: () => void;
  isGenerating?: boolean;
}

export function StoryboardStep({
  storyboard,
  onGenerateStoryboard,
  onGenerateProduction,
  isGenerating = false,
}: StoryboardStepProps) {
  // Debug logging
  console.log('[StoryboardStep] Received storyboard:', storyboard);
  console.log('[StoryboardStep] isGenerating:', isGenerating);
  
  // If no storyboard yet, show generate button
  if (!storyboard) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-8 w-8 text-blue-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Generate Storyboard
              </h3>
              <p className="text-gray-600">
                Create visual storyboard frames from your selected screenplay
              </p>
            </div>
            <button
              onClick={onGenerateStoryboard}
              disabled={isGenerating}
              className="mt-4 px-6 py-3 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors inline-flex items-center"
            >
              {isGenerating ? (
                <>
                  <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Generating...
                </>
              ) : (
                'Generate Storyboard'
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show storyboard
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Storyboard</h2>
            <p className="text-gray-600 mt-1">
              {storyboard.scenes?.length || 0} scenes • Generated{' '}
              {new Date(storyboard.generatedAt).toLocaleDateString()}
            </p>
          </div>
          <button
            onClick={onGenerateProduction}
            disabled={isGenerating}
            className="px-6 py-3 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors inline-flex items-center"
          >
            {isGenerating ? (
              <>
                <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Generating...
              </>
            ) : (
              'Generate Production Pack'
            )}
          </button>
        </div>
      </div>

      {/* Scenes */}
      <div className="space-y-6">
        {storyboard.scenes?.map((scene, index) => (
          <div
            key={index}
            className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
          >
            <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  Scene {scene.sceneNumber}
                </h3>
                <span className="text-sm text-gray-600">
                  {scene.duration}s
                </span>
              </div>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Image - scrollable container */}
                <div className="bg-gray-100 rounded-lg overflow-auto max-h-[500px]">
                  {scene.imageUrl ? (
                    <img
                      src={scene.imageUrl}
                      alt={`Scene ${scene.sceneNumber}`}
                      className="w-full h-auto rounded-lg"
                    />
                  ) : (
                    <div className="aspect-video flex items-center justify-center">
                      <div className="text-center text-gray-400">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="h-12 w-12 mx-auto mb-2"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                          />
                        </svg>
                        <p className="text-sm">Frame {scene.sceneNumber}</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Scene details */}
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">
                      Description
                    </h4>
                    <MarkdownRenderer content={scene.description} className="text-sm" />
                  </div>

                  {scene.dialogue && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">
                        Dialogue
                      </h4>
                      <div className="italic">
                        <MarkdownRenderer content={scene.dialogue} className="text-sm" />
                      </div>
                    </div>
                  )}

                  {scene.cameraAngle && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">
                        Camera
                      </h4>
                      <MarkdownRenderer content={scene.cameraAngle} className="text-sm" />
                    </div>
                  )}

                  {scene.notes && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">
                        Notes
                      </h4>
                      <MarkdownRenderer content={scene.notes} className="text-sm text-gray-600" />
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Mock data notice */}
      {(!storyboard.scenes || storyboard.scenes.length === 0) && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800 text-sm">
            <strong>Mock Mode:</strong> Storyboard generated in mock mode. Connect
            real pipelines to generate actual storyboard frames.
          </p>
        </div>
      )}
    </div>
  );
}
