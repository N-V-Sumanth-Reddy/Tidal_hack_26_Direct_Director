'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import type { GenerationState, WorkflowStep } from '@/lib/types';
import { subscribeToProgress, type GenerationProgress } from '@/lib/sse-client';
import { api } from '@/lib/api';

// ============================================================================
// Types
// ============================================================================

interface GenerationContextValue {
  state: GenerationState;
  startGeneration: (
    step: WorkflowStep,
    params: any
  ) => Promise<{ jobId: string }>;
  cancelGeneration: () => Promise<void>;
  subscribeToProgress: (jobId: string) => void;
  resetState: () => void;
}

// ============================================================================
// Context
// ============================================================================

const GenerationContext = createContext<GenerationContextValue | undefined>(
  undefined
);

// ============================================================================
// Provider
// ============================================================================

interface GenerationProviderProps {
  children: React.ReactNode;
}

const initialState: GenerationState = {
  isGenerating: false,
  step: 'brief',
  progress: 0,
  estimatedTime: 0,
  estimatedCost: 0,
  canCancel: false,
};

export function GenerationProvider({ children }: GenerationProviderProps) {
  const [state, setState] = useState<GenerationState>(initialState);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [unsubscribe, setUnsubscribe] = useState<(() => void) | null>(null);

  /**
   * Start a generation process
   */
  const startGeneration = useCallback(
    async (
      step: WorkflowStep,
      params: any
    ): Promise<{ jobId: string }> => {
      try {
        let response: {
          jobId: string;
          estimatedTime: number;
          estimatedCost: number;
        };

        // Call appropriate API based on step
        switch (step) {
          case 'concept':
            response = await api.generation.generateConcept(params);
            break;
          case 'screenplays':
            response = await api.generation.generateScreenplays(params);
            break;
          case 'storyboard':
            response = await api.generation.generateStoryboard(params);
            break;
          case 'production':
            response = await api.generation.generateProductionPack(params);
            break;
          default:
            throw new Error(`Unsupported generation step: ${step}`);
        }

        // Update state with generation info
        setState({
          isGenerating: true,
          step,
          progress: 0,
          estimatedTime: response.estimatedTime,
          estimatedCost: response.estimatedCost,
          startedAt: new Date(),
          canCancel: true,
        });

        setCurrentJobId(response.jobId);

        return { jobId: response.jobId };
      } catch (error) {
        setState((prev) => ({
          ...prev,
          isGenerating: false,
          error:
            error instanceof Error ? error.message : 'Generation failed',
        }));
        throw error;
      }
    },
    []
  );

  /**
   * Cancel the current generation
   */
  const cancelGeneration = useCallback(async () => {
    if (!currentJobId) return;

    try {
      await api.generation.cancelJob(currentJobId);

      // Unsubscribe from SSE
      if (unsubscribe) {
        unsubscribe();
        setUnsubscribe(null);
      }

      setState((prev) => ({
        ...prev,
        isGenerating: false,
        canCancel: false,
        error: 'Generation cancelled by user',
      }));

      setCurrentJobId(null);
    } catch (error) {
      console.error('Failed to cancel generation:', error);
    }
  }, [currentJobId, unsubscribe]);

  /**
   * Subscribe to generation progress updates via SSE
   */
  const subscribeToProgressUpdates = useCallback(
    (jobId: string) => {
      // Unsubscribe from previous job if any
      if (unsubscribe) {
        unsubscribe();
      }

      const cleanup = subscribeToProgress(
        jobId,
        // onProgress
        (progress: GenerationProgress) => {
          setState((prev) => ({
            ...prev,
            progress: progress.progress,
            estimatedTime: progress.estimatedTimeRemaining || prev.estimatedTime,
          }));
        },
        // onPartial
        (result) => {
          setState((prev) => ({
            ...prev,
            partialResults: result.data,
          }));
        },
        // onComplete
        (result) => {
          setState((prev) => ({
            ...prev,
            isGenerating: false,
            progress: 100,
            canCancel: false,
            partialResults: result,
          }));
          setCurrentJobId(null);
          setUnsubscribe(null);
        },
        // onError
        (error) => {
          setState((prev) => ({
            ...prev,
            isGenerating: false,
            canCancel: false,
            error: error.message,
          }));
          setCurrentJobId(null);
          setUnsubscribe(null);
        }
      );

      setUnsubscribe(() => cleanup);
    },
    [unsubscribe]
  );

  /**
   * Reset generation state
   */
  const resetState = useCallback(() => {
    if (unsubscribe) {
      unsubscribe();
      setUnsubscribe(null);
    }
    setState(initialState);
    setCurrentJobId(null);
  }, [unsubscribe]);

  const value: GenerationContextValue = {
    state,
    startGeneration,
    cancelGeneration,
    subscribeToProgress: subscribeToProgressUpdates,
    resetState,
  };

  return (
    <GenerationContext.Provider value={value}>
      {children}
    </GenerationContext.Provider>
  );
}

// ============================================================================
// Hook
// ============================================================================

export function useGeneration() {
  const context = useContext(GenerationContext);
  if (context === undefined) {
    throw new Error('useGeneration must be used within a GenerationProvider');
  }
  return context;
}

export default GenerationContext;
