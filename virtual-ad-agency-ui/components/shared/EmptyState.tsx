'use client';

import { FileText, FolderOpen, Image, Package } from 'lucide-react';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface EmptyStateProps {
  icon?: 'file' | 'folder' | 'image' | 'package' | React.ReactNode;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

// ============================================================================
// Component
// ============================================================================

const iconMap = {
  file: FileText,
  folder: FolderOpen,
  image: Image,
  package: Package,
};

export function EmptyState({
  icon = 'folder',
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  // Determine icon component
  let IconComponent: React.ReactNode;
  if (typeof icon === 'string' && icon in iconMap) {
    const Icon = iconMap[icon as keyof typeof iconMap];
    IconComponent = <Icon className="h-12 w-12 text-gray-400" />;
  } else {
    IconComponent = icon;
  }

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-12 px-4 text-center',
        className
      )}
    >
      {/* Icon */}
      <div className="mb-4">{IconComponent}</div>

      {/* Title with blur animation */}
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {title}
      </h3>

      {/* Description */}
      <p className="text-sm text-gray-600 max-w-sm mb-6">{description}</p>

      {/* Action Button */}
      {action && (
        <button
          onClick={action.onClick}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}

// ============================================================================
// Preset Empty States
// ============================================================================

export function NoProjectsEmptyState({ onCreate }: { onCreate: () => void }) {
  return (
    <EmptyState
      icon="folder"
      title="No projects yet"
      description="Get started by creating your first ad production project. You'll be guided through brief intake, creative generation, and storyboard development."
      action={{
        label: 'Create New Project',
        onClick: onCreate,
      }}
    />
  );
}

export function NoScenesEmptyState() {
  return (
    <EmptyState
      icon="image"
      title="No scenes generated"
      description="Once you select a screenplay variant, we'll generate a visual storyboard with scene-by-scene images and details."
    />
  );
}

export function NoProductionPackEmptyState() {
  return (
    <EmptyState
      icon="package"
      title="Production pack not generated"
      description="After approving your storyboard, generate a comprehensive production pack including shotlist, budget, schedule, locations, and more."
    />
  );
}

export function NoExportsEmptyState() {
  return (
    <EmptyState
      icon="file"
      title="No exports yet"
      description="Export your storyboard and production documents in various formats (PDF, PNG, JSON, spreadsheet) to share with your team."
    />
  );
}
