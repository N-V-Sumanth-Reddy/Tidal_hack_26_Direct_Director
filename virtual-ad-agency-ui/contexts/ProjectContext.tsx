'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import type { Project, WorkflowStep } from '@/lib/types';

// ============================================================================
// Types
// ============================================================================

interface ProjectContextValue {
  project: Project | null;
  currentStep: WorkflowStep;
  setProject: (project: Project | null) => void;
  setCurrentStep: (step: WorkflowStep) => void;
  isStepLocked: (step: WorkflowStep) => boolean;
  navigateToStep: (step: WorkflowStep) => void;
  updateProject: (updates: Partial<Project>) => void;
}

// ============================================================================
// Context
// ============================================================================

const ProjectContext = createContext<ProjectContextValue | undefined>(
  undefined
);

// ============================================================================
// Provider
// ============================================================================

interface ProjectProviderProps {
  children: React.ReactNode;
  initialProject?: Project | null;
}

export function ProjectProvider({
  children,
  initialProject = null,
}: ProjectProviderProps) {
  const [project, setProject] = useState<Project | null>(initialProject);
  const [currentStep, setCurrentStep] = useState<WorkflowStep>(
    initialProject?.currentStep || 'brief'
  );

  /**
   * Determine if a workflow step is locked based on prerequisites
   */
  const isStepLocked = useCallback(
    (step: WorkflowStep): boolean => {
      if (!project) return true;

      // Define prerequisite rules
      const prerequisites: Record<WorkflowStep, () => boolean> = {
        brief: () => false, // Always unlocked
        concept: () => !!project.brief, // Requires brief
        screenplays: () => !!project.concept, // Requires concept
        select: () =>
          !!project.screenplays && project.screenplays.length === 2, // Requires 2 screenplays
        storyboard: () => !!project.selectedScreenplay, // Requires screenplay selection (HITL gate)
        production: () => !!project.storyboard, // Requires storyboard
        export: () => !!project.productionPack, // Requires production pack
      };

      return !prerequisites[step]?.();
    },
    [project]
  );

  /**
   * Navigate to a workflow step if it's unlocked
   */
  const navigateToStep = useCallback(
    (step: WorkflowStep) => {
      if (!isStepLocked(step)) {
        setCurrentStep(step);
        // Update project's current step
        if (project) {
          setProject({ ...project, currentStep: step });
        }
      }
    },
    [isStepLocked, project]
  );

  /**
   * Update project with partial data
   */
  const updateProject = useCallback(
    (updates: Partial<Project>) => {
      if (project) {
        setProject({ ...project, ...updates });
      }
    },
    [project]
  );

  const value: ProjectContextValue = {
    project,
    currentStep,
    setProject,
    setCurrentStep,
    isStepLocked,
    navigateToStep,
    updateProject,
  };

  return (
    <ProjectContext.Provider value={value}>{children}</ProjectContext.Provider>
  );
}

// ============================================================================
// Hook
// ============================================================================

export function useProject() {
  const context = useContext(ProjectContext);
  if (context === undefined) {
    throw new Error('useProject must be used within a ProjectProvider');
  }
  return context;
}

export default ProjectContext;
