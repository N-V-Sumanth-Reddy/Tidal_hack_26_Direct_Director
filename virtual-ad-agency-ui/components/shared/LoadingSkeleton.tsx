import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

interface LoadingSkeletonProps {
  className?: string;
  variant?: 'text' | 'card' | 'image' | 'circle' | 'button';
  lines?: number;
  animate?: boolean;
}

// ============================================================================
// Component
// ============================================================================

export function LoadingSkeleton({
  className,
  variant = 'text',
  lines = 1,
  animate = true,
}: LoadingSkeletonProps) {
  const baseClasses = cn(
    'bg-gray-200 dark:bg-gray-700',
    animate && 'animate-pulse',
    className
  );

  if (variant === 'text') {
    if (lines === 1) {
      return <div className={cn(baseClasses, 'h-4 rounded')} />;
    }

    return (
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={cn(
              baseClasses,
              'h-4 rounded',
              i === lines - 1 && 'w-3/4' // Last line shorter
            )}
          />
        ))}
      </div>
    );
  }

  if (variant === 'card') {
    return (
      <div className={cn(baseClasses, 'h-48 rounded-lg', className)} />
    );
  }

  if (variant === 'image') {
    return (
      <div className={cn(baseClasses, 'aspect-video rounded-lg', className)} />
    );
  }

  if (variant === 'circle') {
    return (
      <div className={cn(baseClasses, 'h-12 w-12 rounded-full', className)} />
    );
  }

  if (variant === 'button') {
    return (
      <div className={cn(baseClasses, 'h-10 w-24 rounded-md', className)} />
    );
  }

  return <div className={baseClasses} />;
}

// ============================================================================
// Preset Skeletons
// ============================================================================

export function ProjectCardSkeleton() {
  return (
    <div className="rounded-lg border p-6 space-y-4">
      <div className="flex items-start justify-between">
        <div className="space-y-2 flex-1">
          <LoadingSkeleton className="h-6 w-3/4" />
          <LoadingSkeleton className="h-4 w-1/2" />
        </div>
        <LoadingSkeleton variant="circle" className="h-8 w-8" />
      </div>
      <LoadingSkeleton lines={2} />
      <div className="flex gap-2">
        <LoadingSkeleton className="h-6 w-16 rounded-full" />
        <LoadingSkeleton className="h-6 w-20 rounded-full" />
      </div>
    </div>
  );
}

export function StoryboardSceneSkeleton() {
  return (
    <div className="space-y-3">
      <LoadingSkeleton variant="image" />
      <LoadingSkeleton className="h-5 w-1/3" />
      <LoadingSkeleton lines={3} />
    </div>
  );
}

export function ProductionTileSkeleton() {
  return (
    <div className="rounded-lg border p-4 space-y-3">
      <div className="flex items-center justify-between">
        <LoadingSkeleton className="h-5 w-1/3" />
        <LoadingSkeleton className="h-6 w-20 rounded-full" />
      </div>
      <LoadingSkeleton lines={2} />
      <div className="flex items-center gap-2">
        <LoadingSkeleton variant="circle" className="h-4 w-4" />
        <LoadingSkeleton className="h-4 w-32" />
      </div>
    </div>
  );
}

export function ScreenplaySceneSkeleton() {
  return (
    <div className="space-y-3 p-4 border-l-2 border-gray-200">
      <div className="flex items-center gap-3">
        <LoadingSkeleton variant="circle" className="h-8 w-8" />
        <LoadingSkeleton className="h-5 w-1/4" />
      </div>
      <LoadingSkeleton lines={4} />
      <div className="flex gap-2">
        <LoadingSkeleton className="h-4 w-16" />
        <LoadingSkeleton className="h-4 w-20" />
      </div>
    </div>
  );
}
