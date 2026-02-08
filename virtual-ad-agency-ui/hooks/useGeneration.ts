import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { projectKeys } from './useProjects';
import type {
  GenerateConceptRequest,
  GenerateScreenplaysRequest,
  GenerateStoryboardRequest,
  GenerateProductionPackRequest,
  SelectScreenplayRequest,
  RegenerateSceneRequest,
} from '@/lib/types';

// ============================================================================
// Generation Mutations
// ============================================================================

/**
 * Generate concept from brief
 */
export function useGenerateConcept() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: GenerateConceptRequest) => {
      const result = await api.generation.generateConcept(data);
      
      // Poll job status until complete (max 60 seconds)
      const jobId = result.jobId;
      const maxAttempts = 60; // 60 seconds max
      let attempts = 0;
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        try {
          const jobStatus = await api.generation.getJobStatus(jobId);
          console.log(`[Concept Generation] Job status: ${jobStatus.status} (${jobStatus.progress}%)`);
          
          if (jobStatus.status === 'completed') {
            console.log('[Concept Generation] Job completed successfully');
            break;
          } else if (jobStatus.status === 'failed') {
            console.error('[Concept Generation] Job failed:', jobStatus.error);
            throw new Error(jobStatus.error || 'Generation failed');
          }
        } catch (error) {
          console.error('[Concept Generation] Error checking job status:', error);
        }
        
        attempts++;
      }
      
      if (attempts >= maxAttempts) {
        console.warn('[Concept Generation] Polling timeout - job may still be running');
      }
      
      return result;
    },
    onSuccess: (_, variables) => {
      // Invalidate project to refetch with new concept
      queryClient.invalidateQueries({
        queryKey: projectKeys.detail(variables.projectId),
      });
    },
  });
}

/**
 * Generate screenplay variants
 */
export function useGenerateScreenplays() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: GenerateScreenplaysRequest) => {
      const result = await api.generation.generateScreenplays(data);
      
      // Poll job status until complete (max 60 seconds)
      const jobId = result.jobId;
      const maxAttempts = 60;
      let attempts = 0;
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        try {
          const jobStatus = await api.generation.getJobStatus(jobId);
          console.log(`[Screenplay Generation] Job status: ${jobStatus.status} (${jobStatus.progress}%)`);
          
          if (jobStatus.status === 'completed') {
            console.log('[Screenplay Generation] Job completed successfully');
            break;
          } else if (jobStatus.status === 'failed') {
            console.error('[Screenplay Generation] Job failed:', jobStatus.error);
            throw new Error(jobStatus.error || 'Generation failed');
          }
        } catch (error) {
          console.error('[Screenplay Generation] Error checking job status:', error);
        }
        
        attempts++;
      }
      
      return result;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: projectKeys.detail(variables.projectId),
      });
    },
  });
}

/**
 * Select screenplay winner
 */
export function useSelectScreenplay() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SelectScreenplayRequest) =>
      api.selection.selectScreenplay(data),
    onSuccess: (updatedProject) => {
      // Update project cache with selected screenplay
      queryClient.setQueryData(
        projectKeys.detail(updatedProject.id),
        updatedProject
      );
    },
  });
}

/**
 * Generate storyboard from screenplay
 */
export function useGenerateStoryboard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: GenerateStoryboardRequest) => {
      console.log('[useGenerateStoryboard] Starting mutation with data:', data);
      const result = await api.generation.generateStoryboard(data);
      
      // Poll job status until complete (max 60 seconds)
      const jobId = result.jobId;
      const maxAttempts = 60;
      let attempts = 0;
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        try {
          const jobStatus = await api.generation.getJobStatus(jobId);
          console.log(`[Storyboard Generation] Job status: ${jobStatus.status} (${jobStatus.progress}%)`);
          
          if (jobStatus.status === 'completed') {
            console.log('[Storyboard Generation] Job completed successfully');
            break;
          } else if (jobStatus.status === 'failed') {
            console.error('[Storyboard Generation] Job failed:', jobStatus.error);
            throw new Error(jobStatus.error || 'Generation failed');
          }
        } catch (error) {
          console.error('[Storyboard Generation] Error checking job status:', error);
        }
        
        attempts++;
      }
      
      return result;
    },
    onSuccess: (result, variables) => {
      console.log('[useGenerateStoryboard] Mutation succeeded, result:', result);
      console.log('[useGenerateStoryboard] Invalidating queries for project:', variables.projectId);
      queryClient.invalidateQueries({
        queryKey: projectKeys.detail(variables.projectId),
      });
    },
    onError: (error) => {
      console.error('[useGenerateStoryboard] Mutation failed:', error);
    },
  });
}

/**
 * Regenerate a single scene
 */
export function useRegenerateScene() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: RegenerateSceneRequest) =>
      api.generation.regenerateScene(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: projectKeys.detail(variables.projectId),
      });
    },
  });
}

/**
 * Generate production pack
 */
export function useGenerateProductionPack() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: GenerateProductionPackRequest) => {
      const result = await api.generation.generateProductionPack(data);
      
      // Poll job status until complete (max 120 seconds for production pack)
      const jobId = result.jobId;
      const maxAttempts = 120;
      let attempts = 0;
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        try {
          const jobStatus = await api.generation.getJobStatus(jobId);
          console.log(`[Production Pack Generation] Job status: ${jobStatus.status} (${jobStatus.progress}%)`);
          
          if (jobStatus.status === 'completed') {
            console.log('[Production Pack Generation] Job completed successfully');
            break;
          } else if (jobStatus.status === 'failed') {
            console.error('[Production Pack Generation] Job failed:', jobStatus.error);
            throw new Error(jobStatus.error || 'Generation failed');
          }
        } catch (error) {
          console.error('[Production Pack Generation] Error checking job status:', error);
        }
        
        attempts++;
      }
      
      return result;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: projectKeys.detail(variables.projectId),
      });
    },
  });
}

/**
 * Cancel generation job
 */
export function useCancelGeneration() {
  return useMutation({
    mutationFn: (jobId: string) => api.generation.cancelJob(jobId),
  });
}
