import { render, RenderOptions } from '@testing-library/react';
import { ReactElement } from 'react';

// ============================================================================
// Test Utilities
// ============================================================================

/**
 * Custom render function that wraps components with necessary providers
 */
export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, { ...options });
}

/**
 * Helper to wait for async operations
 */
export const waitFor = (ms: number) =>
  new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Mock fetch response helper
 */
export function mockFetchResponse(data: any, ok = true, status = 200) {
  return Promise.resolve({
    ok,
    status,
    json: async () => data,
    text: async () => JSON.stringify(data),
  } as Response);
}

/**
 * Mock fetch error helper
 */
export function mockFetchError(message: string) {
  return Promise.reject(new Error(message));
}
