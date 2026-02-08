'use client';

import { useRouter } from 'next/navigation';
import { ProjectList } from '@/components/projects/ProjectList';
import { useProjects, useCreateProject } from '@/hooks/useProjects';
import { Dock } from '@/components/navigation/Dock';
import type { BudgetBand } from '@/lib/types';

export default function ProjectsPage() {
  const router = useRouter();
  const { data: projects = [], isLoading } = useProjects();
  const createProjectMutation = useCreateProject();

  const handleCreateProject = async () => {
    if (createProjectMutation.isPending) return;

    try {
      const newProject = await createProjectMutation.mutateAsync({
        name: 'New Project',
        client: 'Client Name',
        tags: [],
        budgetBand: 'medium' as BudgetBand,
      });

      // Navigate to the new project workspace
      router.push(`/workspace/${newProject.id}`);
    } catch (error) {
      console.error('Failed to create project:', error);
      alert('Failed to create project. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ProjectList
          projects={projects}
          isLoading={isLoading}
          onCreateProject={handleCreateProject}
        />
      </div>
      <Dock />
    </div>
  );
}
