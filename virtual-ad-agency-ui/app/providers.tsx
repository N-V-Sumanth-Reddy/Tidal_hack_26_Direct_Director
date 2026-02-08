'use client';

import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from '@/lib/query-client';
import { ProjectProvider } from '@/contexts/ProjectContext';
import { GenerationProvider } from '@/contexts/GenerationContext';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <ProjectProvider>
        <GenerationProvider>
          {children}
          <ReactQueryDevtools initialIsOpen={false} />
        </GenerationProvider>
      </ProjectProvider>
    </QueryClientProvider>
  );
}
