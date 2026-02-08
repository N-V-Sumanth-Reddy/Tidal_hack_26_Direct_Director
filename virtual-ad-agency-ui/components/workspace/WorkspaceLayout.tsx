'use client';

import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { Stepper } from '@/components/navigation/Stepper';
import { cn } from '@/lib/utils';
import type { WorkflowStep, Project } from '@/lib/types';

interface WorkspaceLayoutProps {
  project: Project;
  currentStep: WorkflowStep;
  onStepClick: (step: WorkflowStep) => void;
  children: React.ReactNode;
}

export function WorkspaceLayout({
  project,
  currentStep,
  onStepClick,
  children,
}: WorkspaceLayoutProps) {
  // Determine completed and locked steps based on project state
  const completedSteps: WorkflowStep[] = [];
  const lockedSteps: WorkflowStep[] = [];

  // Brief is always unlocked
  if (project.brief) {
    completedSteps.push('brief');
  } else {
    // Lock all steps after brief if brief not submitted
    lockedSteps.push('concept', 'screenplays', 'select', 'storyboard', 'production', 'export');
  }

  // Concept
  if (project.concept) {
    completedSteps.push('concept');
  } else if (!project.brief) {
    lockedSteps.push('concept');
  }

  // Screenplays
  if (project.screenplays && project.screenplays.length > 0) {
    completedSteps.push('screenplays');
  } else if (!project.concept) {
    lockedSteps.push('screenplays', 'select', 'storyboard', 'production', 'export');
  }

  // Select
  if (project.selectedScreenplay) {
    completedSteps.push('select');
  } else if (!project.screenplays || project.screenplays.length === 0) {
    lockedSteps.push('select', 'storyboard', 'production', 'export');
  }

  // Storyboard
  if (project.storyboard) {
    completedSteps.push('storyboard');
  } else if (!project.selectedScreenplay) {
    lockedSteps.push('storyboard', 'production', 'export');
  }

  // Production
  if (project.productionPack) {
    completedSteps.push('production');
  } else if (!project.storyboard) {
    lockedSteps.push('production', 'export');
  }

  // Export is always available once production is complete
  if (project.productionPack) {
    completedSteps.push('export');
  } else {
    lockedSteps.push('export');
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Left Sidebar - Stepper */}
      <aside className="w-64 bg-white border-r flex-shrink-0">
        <div className="sticky top-0 h-screen flex flex-col">
          {/* Header */}
          <div className="p-4 border-b">
            <Link
              href="/projects"
              className={cn(
                'flex items-center gap-2 text-sm text-gray-600',
                'hover:text-gray-900 transition-colors'
              )}
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Projects
            </Link>
            <h2 className="mt-4 text-lg font-semibold text-gray-900 line-clamp-2">
              {project.name}
            </h2>
            <p className="text-sm text-gray-500">{project.client}</p>
          </div>

          {/* Stepper */}
          <div className="flex-1 overflow-y-auto">
            <Stepper
              currentStep={currentStep}
              completedSteps={completedSteps}
              lockedSteps={lockedSteps}
              onStepClick={onStepClick}
            />
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </div>
      </main>
    </div>
  );
}
