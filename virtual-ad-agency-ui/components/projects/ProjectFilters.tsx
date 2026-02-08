'use client';

import { Search, Filter } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ProjectStatus, BudgetBand } from '@/lib/types';

interface ProjectFiltersProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  statusFilter: ProjectStatus | 'all';
  onStatusFilterChange: (status: ProjectStatus | 'all') => void;
  budgetFilter: BudgetBand | 'all';
  onBudgetFilterChange: (budget: BudgetBand | 'all') => void;
}

const STATUS_OPTIONS: Array<{ value: ProjectStatus | 'all'; label: string }> = [
  { value: 'all', label: 'All Status' },
  { value: 'draft', label: 'Draft' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'needs_review', label: 'Needs Review' },
  { value: 'approved', label: 'Approved' },
  { value: 'archived', label: 'Archived' },
];

const BUDGET_OPTIONS: Array<{ value: BudgetBand | 'all'; label: string }> = [
  { value: 'all', label: 'All Budgets' },
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'premium', label: 'Premium' },
];

export function ProjectFilters({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  budgetFilter,
  onBudgetFilterChange,
}: ProjectFiltersProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-4 mb-6">
      {/* Search */}
      <div className="flex-1 relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search projects..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className={cn(
            'w-full pl-10 pr-4 py-2 rounded-lg border',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder:text-gray-400'
          )}
        />
      </div>

      {/* Status Filter */}
      <div className="relative">
        <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
        <select
          value={statusFilter}
          onChange={(e) => onStatusFilterChange(e.target.value as ProjectStatus | 'all')}
          className={cn(
            'pl-10 pr-8 py-2 rounded-lg border appearance-none bg-white',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'cursor-pointer'
          )}
        >
          {STATUS_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Budget Filter */}
      <div className="relative">
        <select
          value={budgetFilter}
          onChange={(e) => onBudgetFilterChange(e.target.value as BudgetBand | 'all')}
          className={cn(
            'pl-4 pr-8 py-2 rounded-lg border appearance-none bg-white',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'cursor-pointer'
          )}
        >
          {BUDGET_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
