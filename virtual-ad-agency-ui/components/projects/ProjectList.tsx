'use client';

import { useState, useMemo } from 'react';
import { Grid, List, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ProjectCard } from './ProjectCard';
import { ProjectFilters } from './ProjectFilters';
import { NoProjectsEmptyState } from '@/components/shared/EmptyState';
import { ProjectCardSkeleton } from '@/components/shared/LoadingSkeleton';
import type { Project, ProjectStatus, BudgetBand } from '@/lib/types';

interface ProjectListProps {
  projects: Project[];
  isLoading?: boolean;
  onCreateProject: () => void;
}

type ViewMode = 'grid' | 'list';

export function ProjectList({ projects, isLoading, onCreateProject }: ProjectListProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<ProjectStatus | 'all'>('all');
  const [budgetFilter, setBudgetFilter] = useState<BudgetBand | 'all'>('all');

  // Filter projects
  const filteredProjects = useMemo(() => {
    return projects.filter((project) => {
      // Search filter
      const matchesSearch =
        searchQuery === '' ||
        project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        project.client.toLowerCase().includes(searchQuery.toLowerCase()) ||
        project.tags?.some((tag) =>
          tag.toLowerCase().includes(searchQuery.toLowerCase())
        );

      // Status filter
      const matchesStatus = statusFilter === 'all' || project.status === statusFilter;

      // Budget filter
      const matchesBudget =
        budgetFilter === 'all' || project.budgetBand === budgetFilter;

      return matchesSearch && matchesStatus && matchesBudget;
    });
  }, [projects, searchQuery, statusFilter, budgetFilter]);

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <ProjectCardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  // Empty state
  if (projects.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
        </div>
        <NoProjectsEmptyState onCreate={onCreateProject} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
        <button
          onClick={onCreateProject}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg',
            'bg-blue-500 text-white font-medium',
            'hover:bg-blue-600 transition-colors',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
          )}
        >
          <Plus className="h-5 w-5" />
          New Project
        </button>
      </div>

      {/* Filters */}
      <ProjectFilters
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
        budgetFilter={budgetFilter}
        onBudgetFilterChange={setBudgetFilter}
      />

      {/* View Toggle */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600">
          {filteredProjects.length} {filteredProjects.length === 1 ? 'project' : 'projects'}
        </p>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode('grid')}
            className={cn(
              'p-2 rounded-lg transition-colors',
              viewMode === 'grid'
                ? 'bg-blue-100 text-blue-600'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            )}
            aria-label="Grid view"
            aria-pressed={viewMode === 'grid'}
          >
            <Grid className="h-5 w-5" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={cn(
              'p-2 rounded-lg transition-colors',
              viewMode === 'list'
                ? 'bg-blue-100 text-blue-600'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            )}
            aria-label="List view"
            aria-pressed={viewMode === 'list'}
          >
            <List className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Projects Grid/List */}
      {filteredProjects.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No projects match your filters</p>
          <button
            onClick={() => {
              setSearchQuery('');
              setStatusFilter('all');
              setBudgetFilter('all');
            }}
            className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
          >
            Clear filters
          </button>
        </div>
      ) : (
        <div
          className={cn(
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
              : 'flex flex-col gap-4'
          )}
        >
          {filteredProjects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}
    </div>
  );
}
