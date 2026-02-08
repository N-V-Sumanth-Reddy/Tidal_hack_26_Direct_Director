# Implementation Plan: Virtual Ad Agency Workspace UI

## Overview

This implementation plan breaks down the virtual ad agency workspace UI into discrete, incremental tasks. The approach follows a bottom-up strategy: establish the foundation (project setup, types, API layer), build core components, implement workflow steps, add production pack features, and finally integrate React Bits animations and accessibility features.

Each task builds on previous work, with testing integrated throughout to catch issues early. The plan includes checkpoint tasks to ensure stability before moving to the next phase.

## Tasks

- [x] 1. Project setup and foundation
  - [x] 1.1 Initialize Next.js project with TypeScript and Tailwind CSS
    - Create Next.js 14+ project with App Router
    - Configure TypeScript with strict mode
    - Set up Tailwind CSS and configure theme
    - Install shadcn/ui and configure components
    - Install React Bits library
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [x] 1.2 Define core TypeScript types and interfaces
    - Create types.ts with Project, Brief, Concept, Screenplay, Storyboard, ProductionPack interfaces
    - Define WorkflowStep, ProjectStatus, DocumentType, DocumentStatus enums
    - Define API request/response types
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1_

  - [x] 1.3 Set up testing framework
    - Install Vitest, React Testing Library, and fast-check
    - Configure vitest.config.ts with jsdom environment
    - Create test setup file with custom matchers
    - Create test generators for domain objects (Project, Brief, etc.)
    - _Requirements: All (testing foundation)_

  - [ ]* 1.4 Write property test for type generators
    - **Property: Generated test data should match type constraints**
    - **Validates: Requirements N/A (test infrastructure)**

- [x] 2. API layer and backend integration
  - [x] 2.1 Create API client with REST endpoints
    - Implement api.ts with fetch wrapper
    - Create endpoints for projects CRUD operations
    - Create endpoints for generation (concept, screenplay, storyboard, production)
    - Add error handling and response parsing
    - _Requirements: 12.1, 12.2, 12.3, 12.4_

  - [ ]* 2.2 Write property test for API request parameter completeness
    - **Property 32: Generation request parameter completeness**
    - **Validates: Requirements 12.2**

  - [x] 2.3 Implement Server-Sent Events (SSE) for streaming
    - Create SSE client for generation progress
    - Handle connection management and reconnection
    - Parse streaming updates and partial results
    - _Requirements: 12.5, 7.3_

  - [ ]* 2.4 Write property test for streaming response handling
    - **Property 35: Streaming response handling**
    - **Validates: Requirements 12.5**

  - [x] 2.5 Implement authentication and session management
    - Add token storage and retrieval
    - Add authentication headers to all requests
    - Handle token refresh and expiration
    - _Requirements: 12.6_

  - [ ]* 2.6 Write property test for authentication persistence
    - **Property 36: Authentication persistence**
    - **Validates: Requirements 12.6**

- [ ] 3. Checkpoint - API layer complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. State management with React Context
  - [x] 4.1 Create ProjectContext for project state
    - Implement ProjectContext with project data, current step, and navigation
    - Add isStepLocked function based on workflow prerequisites
    - Add updateProject mutation function
    - _Requirements: 6.1, 6.4, 6.5_

  - [ ]* 4.2 Write property test for prerequisite-based step locking
    - **Property 17: Prerequisite-based step locking**
    - **Validates: Requirements 6.5**

  - [x] 4.3 Create GenerationContext for generation state
    - Implement GenerationContext with generation state, progress, and controls
    - Add startGeneration function with cost/time estimation
    - Add cancelGeneration function
    - Add subscribeToProgress for SSE updates
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ]* 4.4 Write property test for generation progress display
    - **Property 20: Active generation shows progress**
    - **Validates: Requirements 7.2**

- [x] 5. React Query setup for server state
  - [x] 5.1 Configure React Query client
    - Set up QueryClient with caching and refetch policies
    - Create custom hooks: useProjects, useProject, useGeneration
    - Implement optimistic updates for mutations
    - _Requirements: 1.1, 1.3_

  - [ ]* 5.2 Write unit tests for React Query hooks
    - Test data fetching, caching, and mutations
    - Test error handling and retry logic
    - _Requirements: 1.1, 1.3_

- [x] 6. Shared UI components
  - [x] 6.1 Create LoadingSkeleton component
    - Implement skeleton screens for different content types
    - Add shimmer animation
    - _Requirements: 7.5_

  - [x] 6.2 Create ProgressIndicator component
    - Display progress bar with percentage
    - Show estimated time and cost
    - Add cancel button
    - _Requirements: 7.1, 7.2_

  - [x] 6.3 Create StreamingText component
    - Display text with typing animation as it streams
    - Handle partial updates
    - _Requirements: 7.3_

  - [x] 6.4 Create WarningBanner component
    - Display warnings with severity levels
    - Support different categories (legal, brand, location, budget, risk)
    - Add dismiss functionality
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ]* 6.5 Write property test for warning display
    - **Property 28: Warning display for detected issues**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4**

  - [x] 6.6 Create EmptyState component with React Bits BlurText
    - Use BlurText for animated guidance text
    - Add illustration or icon
    - _Requirements: 1.5, 8.4_

  - [ ]* 6.7 Write unit tests for shared components
    - Test rendering with different props
    - Test user interactions
    - _Requirements: 7.1, 7.2, 7.3, 10.1_

- [ ] 7. Navigation components
  - [x] 7.1 Create Dock component with React Bits
    - Integrate React Bits Dock for primary navigation
    - Add routes: Projects, Workspace, Assets, Settings
    - Implement active state highlighting
    - Add tooltips
    - _Requirements: 8.1_

  - [x] 7.2 Create Stepper component for workflow navigation
    - Display all workflow steps (Brief, Concept, Screenplays, Select, Storyboard, Production, Export)
    - Highlight current active step
    - Show completed steps with checkmarks
    - Show locked steps with lock icons
    - Handle step click navigation
    - _Requirements: 6.1, 6.2, 6.4, 6.7_

  - [ ]* 7.3 Write property test for stepper highlighting
    - **Property 15: Stepper highlights current step**
    - **Validates: Requirements 6.2**

  - [ ]* 7.4 Write property test for step navigation locks
    - **Property 16: Step navigation respects locks**
    - **Validates: Requirements 6.4**

  - [ ]* 7.5 Write property test for locked step visual indication
    - **Property 18: Locked step visual indication**
    - **Validates: Requirements 6.7**

- [ ] 8. Project list and management
  - [x] 8.1 Create ProjectList component
    - Display projects in table/grid view
    - Add view toggle button
    - Show project metadata (status, client, date, budget band)
    - Add "New Project" button
    - _Requirements: 1.1, 1.4, 1.6_

  - [ ]* 8.2 Write property test for project metadata completeness
    - **Property 2: Project metadata completeness**
    - **Validates: Requirements 1.4**

  - [x] 8.3 Create ProjectFilters component
    - Add filters for status, client, date, budget band
    - Add search input
    - Implement filter logic
    - _Requirements: 1.1, 1.3_

  - [ ]* 8.4 Write property test for search and filter
    - **Property 1: Search and filter results match criteria**
    - **Validates: Requirements 1.3**

  - [x] 8.5 Create ProjectCard component
    - Display project summary with metadata
    - Add click handler to open workspace
    - Show status badge
    - _Requirements: 1.1, 1.4_

  - [ ]* 8.6 Write unit tests for project list components
    - Test empty state display
    - Test view toggle
    - Test navigation to new project
    - _Requirements: 1.1, 1.2, 1.5, 1.6_

- [ ] 9. Checkpoint - Navigation and project list complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Brief intake step
  - [x] 10.1 Create BriefStep component
    - Create form with fields: platform, duration, budget, location, constraints, creative direction, brand mandatories, target audience
    - Add form validation
    - Add submit button to trigger concept generation
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ]* 10.2 Write property test for brief validation
    - **Property 3: Brief validation rejects incomplete submissions**
    - **Validates: Requirements 2.3**

  - [ ]* 10.3 Write property test for brief API requests
    - **Property 4: Brief API requests include all parameters**
    - **Validates: Requirements 2.4**

  - [ ]* 10.4 Write property test for brief persistence
    - **Property 5: Brief data persistence round-trip**
    - **Validates: Requirements 2.5**

  - [ ]* 10.5 Write property test for constraint change marking
    - **Property 6: Constraint changes mark downstream steps**
    - **Validates: Requirements 2.6**

- [ ] 11. Concept and screenplay steps
  - [x] 11.1 Create ConceptStep component
    - Display generated concept (title, description, key message, visual style)
    - Show generation progress while loading
    - Add "Generate Screenplays" button
    - _Requirements: 3.1, 3.2_

  - [x] 11.2 Create ScreenplayCompare component
    - Display two screenplay variants side-by-side
    - Show scene-by-scene comparison
    - Highlight differences
    - Display scoring chips (clarity, feasibility, cost risk)
    - Add "Select Winner" buttons
    - _Requirements: 3.4, 3.5, 3.6_

  - [ ]* 11.3 Write property test for screenplay scoring display
    - **Property 7: Screenplay comparison displays all scores**
    - **Validates: Requirements 3.5**

  - [ ]* 11.4 Write property test for HITL gate enforcement
    - **Property 8: HITL gate enforcement**
    - **Validates: Requirements 3.7**

  - [ ]* 11.5 Write unit tests for concept and screenplay components
    - Test concept display
    - Test screenplay comparison rendering
    - Test selection interaction
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6_

- [ ] 12. Storyboard viewer
  - [ ] 12.1 Create StoryboardViewer component
    - Display scene list with thumbnail images
    - Add click handler to open scene details
    - Show consistency controls (style lock, character lock)
    - Add download buttons (PDF, PNG pack, JSON)
    - _Requirements: 4.2, 4.4, 4.6_

  - [ ] 12.2 Create SceneDetail component
    - Display scene image
    - Show visual description, camera angle, camera movement, on-screen text, audio notes
    - Add "Regenerate Scene" button
    - _Requirements: 4.3, 4.5_

  - [ ]* 12.3 Write property test for scene detail completeness
    - **Property 9: Scene detail completeness**
    - **Validates: Requirements 4.3**

  - [ ]* 12.4 Write property test for scene regeneration isolation
    - **Property 10: Scene regeneration isolation**
    - **Validates: Requirements 4.5**

  - [ ]* 12.5 Write unit tests for storyboard components
    - Test scene list rendering
    - Test scene detail modal
    - Test consistency controls
    - Test download actions
    - _Requirements: 4.1, 4.2, 4.4, 4.6_

- [ ] 13. Checkpoint - Workflow steps through storyboard complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Production pack dashboard
  - [ ] 14.1 Create ProductionPackDashboard component
    - Display tiles for all document types (Shotlist, Locations, Budget, Schedule, Casting, Props/Wardrobe, Legal, Risk)
    - Use React Bits MagicBento for tiles
    - Show top 3 risks prominently
    - Add "Regenerate Production Pack" button
    - _Requirements: 5.2, 5.7_

  - [ ] 14.2 Create ProductionTile component with React Bits MagicBento
    - Display document status (Draft/Needs Review/Approved)
    - Show last updated timestamp
    - Display warnings count
    - Add click handler to open document
    - _Requirements: 5.3_

  - [ ]* 14.3 Write property test for production tile information
    - **Property 11: Production tile information completeness**
    - **Validates: Requirements 5.3**

  - [ ]* 14.4 Write property test for top risks visibility
    - **Property 14: Top risks visibility**
    - **Validates: Requirements 5.7**

  - [ ]* 14.5 Write unit tests for production pack dashboard
    - Test tile rendering
    - Test document opening
    - Test regeneration trigger
    - _Requirements: 5.1, 5.2_

- [ ] 15. Production pack editors
  - [ ] 15.1 Create BudgetEditor component
    - Display budget data in spreadsheet-like table
    - Allow inline editing
    - Calculate totals automatically
    - _Requirements: 5.4_

  - [ ] 15.2 Create ScheduleEditor component
    - Display schedule data in spreadsheet-like table
    - Allow inline editing
    - Show timeline visualization
    - _Requirements: 5.4_

  - [ ] 15.3 Create AssumptionsPanel component
    - Display all assumptions with original values
    - Show user overrides
    - Allow editing assumptions
    - Track editor and timestamp
    - _Requirements: 5.5_

  - [ ]* 15.4 Write property test for assumption override tracking
    - **Property 12: Assumption override tracking**
    - **Validates: Requirements 5.5**

  - [ ] 15.5 Create ChangelogViewer component
    - Display changelog entries
    - Show what changed and when
    - Group by document type
    - _Requirements: 5.6_

  - [ ]* 15.6 Write property test for regeneration changelog
    - **Property 13: Regeneration produces changelog**
    - **Validates: Requirements 5.6**

  - [ ]* 15.7 Write unit tests for production pack editors
    - Test budget editing
    - Test schedule editing
    - Test assumptions editing
    - Test changelog display
    - _Requirements: 5.4, 5.5, 5.6_

- [ ] 16. Context panel and workspace layout
  - [ ] 16.1 Create ContextPanel component
    - Display assumptions
    - Display constraints
    - Display brand mandatories
    - Display warnings aggregated from all sources
    - _Requirements: 6.3, 10.5_

  - [ ]* 16.2 Write property test for warning aggregation
    - **Property 29: Warning aggregation in dashboard**
    - **Validates: Requirements 10.5**

  - [x] 16.3 Create WorkspaceLayout component
    - Integrate Stepper navigation on left
    - Display active step content in center
    - Display ContextPanel on right
    - Add version history controls
    - _Requirements: 6.1, 6.3, 6.6_

  - [ ]* 16.4 Write unit tests for workspace layout
    - Test layout rendering
    - Test step navigation
    - Test context panel display
    - _Requirements: 6.1, 6.3, 6.6_

- [ ] 17. Export functionality
  - [ ] 17.1 Create ExportStep component
    - Display export options for storyboard (PDF, PNG pack, JSON)
    - Display export options for production pack (PDF, spreadsheet)
    - Add export buttons with progress indication
    - Show export history
    - _Requirements: 11.1, 11.2, 11.3, 11.5_

  - [ ]* 17.2 Write property test for export file generation
    - **Property 30: Export generates files and links**
    - **Validates: Requirements 11.4**

  - [ ]* 17.3 Write property test for export history tracking
    - **Property 31: Export history tracking**
    - **Validates: Requirements 11.5**

  - [ ]* 17.4 Write unit tests for export functionality
    - Test export option display
    - Test export triggering
    - Test download link generation
    - Test history display
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 18. Checkpoint - All workflow steps and production pack complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 19. Accessibility implementation
  - [ ] 19.1 Add keyboard navigation support
    - Implement keyboard handlers for Dock (Tab, Arrow keys)
    - Implement keyboard handlers for Stepper (Tab, Arrow keys, Enter)
    - Add focus management for modals and dialogs
    - _Requirements: 9.1_

  - [ ]* 19.2 Write property test for keyboard navigation
    - **Property 24: Keyboard navigation completeness**
    - **Validates: Requirements 9.1**

  - [ ] 19.3 Add focus indicators
    - Add visible focus rings to all interactive elements
    - Style focus states with high contrast
    - _Requirements: 9.2_

  - [ ]* 19.4 Write property test for focus indicators
    - **Property 25: Focus indicator visibility**
    - **Validates: Requirements 9.2**

  - [ ] 19.5 Ensure color contrast compliance
    - Audit all text/background combinations
    - Adjust colors to meet WCAG AA standards
    - _Requirements: 9.3_

  - [ ]* 19.6 Write property test for color contrast
    - **Property 26: Color contrast compliance**
    - **Validates: Requirements 9.3**

  - [ ] 19.7 Add ARIA labels and semantic HTML
    - Add ARIA labels to icon buttons
    - Use semantic HTML elements (nav, main, aside, article)
    - Add ARIA live regions for dynamic content
    - _Requirements: 9.5_

  - [ ]* 19.8 Write property test for ARIA labels
    - **Property 27: ARIA label presence**
    - **Validates: Requirements 9.5**

  - [ ]* 19.9 Run accessibility audit with axe
    - Test all major components with axe-core
    - Fix any violations
    - _Requirements: 9.1, 9.2, 9.3, 9.5_

- [ ] 20. Reduced motion support
  - [ ] 20.1 Implement prefers-reduced-motion detection
    - Add CSS media query for prefers-reduced-motion
    - Create useReducedMotion hook
    - _Requirements: 8.5, 9.4_

  - [ ] 20.2 Update all animations to respect reduced motion
    - Disable or reduce animations in React Bits components
    - Disable or reduce custom animations
    - Ensure functionality remains without animations
    - _Requirements: 8.5, 9.4_

  - [ ]* 20.3 Write property test for reduced motion support
    - **Property 23: Reduced motion support**
    - **Validates: Requirements 8.5, 9.4**

- [ ] 21. Error handling and user feedback
  - [ ] 21.1 Implement error boundaries
    - Create ErrorBoundary component
    - Add fallback UI for errors
    - Add error logging
    - _Requirements: 12.4_

  - [ ] 21.2 Add user-friendly error messages
    - Map backend error codes to user-friendly messages
    - Add retry mechanisms
    - Add support contact information
    - _Requirements: 12.4_

  - [ ]* 21.3 Write property test for error message display
    - **Property 34: Error message user-friendliness**
    - **Validates: Requirements 12.4**

  - [ ] 21.4 Implement partial failure handling
    - Display which generation steps succeeded/failed
    - Preserve successful partial results
    - Offer retry for failed steps
    - _Requirements: 7.4_

  - [ ]* 21.5 Write property test for partial failure indication
    - **Property 22: Partial failure indication**
    - **Validates: Requirements 7.4**

- [ ] 22. API response parsing and validation
  - [ ] 22.1 Add response validation with Zod
    - Define Zod schemas for all API responses
    - Validate responses before using data
    - Handle validation errors gracefully
    - _Requirements: 12.3_

  - [ ]* 22.2 Write property test for API response parsing
    - **Property 33: API response parsing**
    - **Validates: Requirements 12.3**

- [ ] 23. Generation cost and time estimation
  - [ ] 23.1 Implement cost/time estimation display
    - Fetch estimates from backend before generation
    - Display estimates in modal before confirming
    - Show running costs during generation
    - _Requirements: 7.1_

  - [ ]* 23.2 Write property test for estimation display
    - **Property 19: Generation displays cost and time estimates**
    - **Validates: Requirements 7.1**

- [ ] 24. Streaming results display
  - [ ] 24.1 Implement incremental result display
    - Update UI as streaming data arrives
    - Show partial concept/screenplay text
    - Show partial storyboard scenes
    - _Requirements: 7.3_

  - [ ]* 24.2 Write property test for streaming display
    - **Property 21: Streaming results display incrementally**
    - **Validates: Requirements 7.3**

- [ ] 25. Final checkpoint - All features complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 26. Integration testing and polish
  - [ ]* 26.1 Write end-to-end integration tests
    - Test complete project creation flow
    - Test brief → concept → screenplay → storyboard → production → export
    - Test error recovery flows
    - Test concurrent user actions
    - _Requirements: All_

  - [ ] 26.2 Performance optimization
    - Add React.memo to expensive components
    - Implement virtual scrolling for long lists
    - Optimize image loading with lazy loading
    - Add code splitting for routes
    - _Requirements: All_

  - [ ] 26.3 Visual polish and responsive design
    - Ensure responsive layout for tablet and desktop
    - Add loading transitions
    - Polish animations and micro-interactions
    - Test on different browsers
    - _Requirements: All_

  - [ ]* 26.4 Run full test suite
    - Run all unit tests
    - Run all property tests with 1000 iterations
    - Run accessibility tests
    - Generate coverage report
    - _Requirements: All_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation throughout development
- Property tests validate universal correctness properties with 100+ iterations
- Unit tests validate specific examples, edge cases, and integration points
- The implementation uses TypeScript, Next.js, Tailwind CSS, shadcn/ui, and React Bits
- Backend integration assumes existing Python services (ad_video_pipeline.py, ad_production_pipeline.py)
