'use client';

import { use, useState } from 'react';
import { useRouter } from 'next/navigation';
import { WorkspaceLayout } from '@/components/workspace/WorkspaceLayout';
import { BriefStep } from '@/components/workspace/steps/BriefStep';
import { ConceptStep } from '@/components/workspace/steps/ConceptStep';
import { ScreenplayCompare } from '@/components/workspace/steps/ScreenplayCompare';
import { StoryboardStep } from '@/components/workspace/steps/StoryboardStep';
import { ProductionStep } from '@/components/workspace/steps/ProductionStep';
import { ExportStep } from '@/components/workspace/steps/ExportStep';
import { useProject } from '@/hooks/useProjects';
import {
  useGenerateConcept,
  useGenerateScreenplays,
  useSelectScreenplay,
  useGenerateStoryboard,
  useGenerateProductionPack,
} from '@/hooks/useGeneration';
import { api } from '@/lib/api';
import type { WorkflowStep, Brief } from '@/lib/types';

interface WorkspacePageProps {
  params: Promise<{ projectId: string }>;
}

export default function WorkspacePage({ params }: WorkspacePageProps) {
  const { projectId } = use(params);
  const router = useRouter();
  
  // Queries
  const { data: project, isLoading } = useProject(projectId);
  
  // Mutations
  const generateConceptMutation = useGenerateConcept();
  const generateScreenplaysMutation = useGenerateScreenplays();
  const selectScreenplayMutation = useSelectScreenplay();
  const generateStoryboardMutation = useGenerateStoryboard();
  const generateProductionMutation = useGenerateProductionPack();

  const [currentStep, setCurrentStep] = useState<WorkflowStep>('brief');

  // Handle step navigation
  const handleStepClick = (step: WorkflowStep) => {
    setCurrentStep(step);
  };

  // Handle brief submission
  const handleBriefSubmit = async (brief: Brief) => {
    try {
      // Submit brief
      await api.brief.submit(projectId, { brief });
      
      // Start concept generation
      await generateConceptMutation.mutateAsync({ projectId, brief });
      
      setCurrentStep('concept');
    } catch (error) {
      console.error('Failed to submit brief:', error);
      alert('Failed to submit brief. Please try again.');
    }
  };

  // Handle screenplay generation
  const handleGenerateScreenplays = async () => {
    if (!project?.concept) return;
    
    try {
      await generateScreenplaysMutation.mutateAsync({
        projectId,
        conceptId: project.concept.id,
      });
      setCurrentStep('screenplays');
    } catch (error) {
      console.error('Failed to generate screenplays:', error);
      alert('Failed to generate screenplays. Please try again.');
    }
  };

  // Handle screenplay selection
  const handleScreenplaySelect = async (screenplayId: string) => {
    try {
      await selectScreenplayMutation.mutateAsync({ projectId, screenplayId });
      setCurrentStep('storyboard');
    } catch (error) {
      console.error('Failed to select screenplay:', error);
      alert('Failed to select screenplay. Please try again.');
    }
  };

  // Handle storyboard generation
  const handleGenerateStoryboard = async () => {
    if (!project?.selectedScreenplay) {
      alert('Please select a screenplay first.');
      return;
    }
    
    console.log('[WorkspacePage] Starting storyboard generation for project:', projectId);
    try {
      await generateStoryboardMutation.mutateAsync({ 
        projectId, 
        screenplayId: project.selectedScreenplay 
      });
      console.log('[WorkspacePage] Storyboard generation completed successfully');
      // Stay on storyboard step to view results
    } catch (error) {
      console.error('Failed to generate storyboard:', error);
      alert('Failed to generate storyboard. Please try again.');
    }
  };

  // Handle production pack generation
  const handleGenerateProduction = async () => {
    if (!project?.storyboard?.id) {
      alert('Please generate a storyboard first.');
      return;
    }
    
    try {
      await generateProductionMutation.mutateAsync({ 
        projectId, 
        storyboardId: project.storyboard.id 
      });
      setCurrentStep('production');
    } catch (error) {
      console.error('Failed to generate production pack:', error);
      alert('Failed to generate production pack. Please try again.');
    }
  };

  // Handle export
  const handleExport = () => {
    setCurrentStep('export');
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading project...</p>
        </div>
      </div>
    );
  }

  // Project not found
  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Project Not Found</h2>
          <p className="text-gray-600 mb-6">
            The project you're looking for doesn't exist or has been deleted.
          </p>
          <button
            onClick={() => router.push('/projects')}
            className="px-6 py-3 rounded-lg bg-blue-500 text-white font-medium hover:bg-blue-600 transition-colors"
          >
            Back to Projects
          </button>
        </div>
      </div>
    );
  }

  // Render current step content
  const renderStepContent = () => {
    const isGenerating =
      generateConceptMutation.isPending ||
      generateScreenplaysMutation.isPending ||
      selectScreenplayMutation.isPending ||
      generateStoryboardMutation.isPending ||
      generateProductionMutation.isPending;

    switch (currentStep) {
      case 'brief':
        return (
          <BriefStep
            brief={project.brief}
            onSubmit={handleBriefSubmit}
            isSubmitting={generateConceptMutation.isPending}
          />
        );

      case 'concept':
        return (
          <ConceptStep
            concept={project.concept}
            onGenerateScreenplays={handleGenerateScreenplays}
            isGenerating={generateScreenplaysMutation.isPending}
          />
        );

      case 'screenplays':
      case 'select':
        if (project.screenplays && project.screenplays.length >= 2) {
          const screenplay1 = project.screenplays[0];
          const screenplay2 = project.screenplays[1];
          if (screenplay1 && screenplay2) {
            return (
              <ScreenplayCompare
                screenplays={[screenplay1, screenplay2]}
                selectedId={project.selectedScreenplay}
                onSelect={handleScreenplaySelect}
                isSelecting={selectScreenplayMutation.isPending}
              />
            );
          }
        }
        return (
          <div className="max-w-3xl">
            <div className="bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No Screenplays Yet
              </h3>
              <p className="text-gray-600">
                Generate a concept first, then create screenplay variants.
              </p>
            </div>
          </div>
        );

      case 'storyboard':
        return (
          <StoryboardStep
            storyboard={project.storyboard}
            onGenerateStoryboard={handleGenerateStoryboard}
            onGenerateProduction={handleGenerateProduction}
            isGenerating={generateStoryboardMutation.isPending}
          />
        );

      case 'production':
        return (
          <ProductionStep
            productionPack={project.productionPack}
            onGenerateProduction={handleGenerateProduction}
            onExport={handleExport}
            isGenerating={generateProductionMutation.isPending}
          />
        );

      case 'export':
        return (
          <ExportStep
            projectId={projectId}
            projectName={project.name}
          />
        );

      default:
        return null;
    }
  };

  return (
    <WorkspaceLayout
      project={project}
      currentStep={currentStep}
      onStepClick={handleStepClick}
    >
      {renderStepContent()}
    </WorkspaceLayout>
  );
}
