'use client';

import { Calendar, User, Tag } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import type { Project, ProjectStatus } from '@/lib/types';

interface ProjectCardProps {
  project: Project;
}

const STATUS_STYLES: Record<ProjectStatus, { bg: string; text: string; label: string }> = {
  draft: { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Draft' },
  in_progress: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'In Progress' },
  needs_review: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'Needs Review' },
  approved: { bg: 'bg-green-100', text: 'text-green-700', label: 'Approved' },
  archived: { bg: 'bg-gray-100', text: 'text-gray-500', label: 'Archived' },
};

export function ProjectCard({ project }: ProjectCardProps) {
  const statusStyle = STATUS_STYLES[project.status];
  const formattedDate = new Date(project.createdAt).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  return (
    <Link
      href={`/workspace/${project.id}`}
      className={cn(
        'block p-6 rounded-lg border bg-white',
        'hover:border-blue-300 hover:shadow-md',
        'transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900 line-clamp-1">
          {project.name}
        </h3>
        <span
          className={cn(
            'px-2.5 py-1 rounded-full text-xs font-medium',
            statusStyle.bg,
            statusStyle.text
          )}
        >
          {statusStyle.label}
        </span>
      </div>

      {/* Client */}
      <div className="flex items-center gap-2 text-sm text-gray-600 mb-3">
        <User className="h-4 w-4" />
        <span>{project.client}</span>
      </div>

      {/* Tags */}
      {project.tags && project.tags.length > 0 && (
        <div className="flex items-center gap-2 mb-3 flex-wrap">
          <Tag className="h-4 w-4 text-gray-400" />
          {project.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-600"
            >
              {tag}
            </span>
          ))}
          {project.tags.length > 3 && (
            <span className="text-xs text-gray-500">
              +{project.tags.length - 3} more
            </span>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t">
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Calendar className="h-4 w-4" />
          <span>{formattedDate}</span>
        </div>
        {project.budgetBand && (
          <span className="text-xs font-medium text-gray-600 uppercase">
            {project.budgetBand}
          </span>
        )}
      </div>
    </Link>
  );
}
