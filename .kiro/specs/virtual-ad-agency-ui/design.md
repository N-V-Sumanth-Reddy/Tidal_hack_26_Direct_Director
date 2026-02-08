# Design Document: Virtual Ad Agency Workspace UI

## Overview

The virtual ad agency workspace UI is a Next.js application that provides an intuitive, step-based interface for managing ad production workflows. The application guides users through a structured pipeline from initial brief intake through creative generation, storyboard development, and production planning, with clear human-in-the-loop (HITL) decision points.

The UI integrates with existing Python backend services (ad_video_pipeline.py, ad_production_pipeline.py) that handle AI-powered content generation. The frontend focuses on state management, user interaction, progress visualization, and document presentation.

Key design principles:
- **Guided workflow**: Step-based navigation prevents users from getting lost
- **Transparency**: Show costs, time estimates, and progress for all generation operations
- **HITL gates**: Require explicit user approval at critical decision points
- **Accessibility first**: Keyboard navigation, screen reader support, reduced motion support
- **Motion with purpose**: Animations communicate state changes and system activity

## Architecture

### Technology Stack

- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Component Library**: shadcn/ui (base components)
- **Animation Library**: React Bits (Dock, MagicBento, LogoLoop, BlurText)
- **State Management**: React Context + hooks for local state, React Query for server state
- **Backend Communication**: REST API with fetch/axios, Server-Sent Events (SSE) for streaming

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Next.js Application                      │
├─────────────────────────────────────────────────────────────┤
│  Pages/Routes                                                │
│  ├─ /projects (list)                                         │
│  ├─ /projects/[id] (workspace)                               │
│  ├─ /assets                                                  │
│  └─ /settings                                                │
├─────────────────────────────────────────────────────────────┤
│  Components                                                   │
│  ├─ Navigation (Dock, Stepper)                               │
│  ├─ Project Management (List, Filters, Cards)                │
│  ├─ Workflow Steps (Brief, Concept, Screenplay, etc.)        │
│  ├─ Production Pack (Dashboard, Editors, Tiles)              │
│  └─ Shared (Loading, Errors, Warnings, Modals)               │
├─────────────────────────────────────────────────────────────┤
│  State Management                                             │
│  ├─ ProjectContext (current project, step, locks)            │
│  ├─ GenerationContext (progress, costs, cancellation)        │
│  └─ React Query (server state, caching, mutations)           │
├─────────────────────────────────────────────────────────────┤
│  API Layer                                                    │
│  ├─ REST endpoints (/api/projects, /api/generate, etc.)      │
│  ├─ SSE endpoints (/api/stream/generation)                   │
│  └─ Backend integration (Python pipeline proxy)              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Python Backend Services (Existing)              │
│  ├─ ad_video_pipeline.py                                     │
│  └─ ad_production_pipeline.py                                │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
virtual-ad-agency-ui/
├── src/
│   ├── app/
│   │   ├── projects/
│   │   │   ├── page.tsx                 # Project list
│   │   │   └── [id]/
│   │   │       └── page.tsx             # Project workspace
│   │   ├── assets/
│   │   │   └── page.tsx
│   │   ├── settings/
│   │   │   └── page.tsx
│   │   ├── api/
│   │   │   ├── projects/
│   │   │   ├── generate/
│   │   │   └── stream/
│   │   ├── layout.tsx
│   │   └── page.tsx                     # Landing/home
│   ├── components/
│   │   ├── navigation/
│   │   │   ├── Dock.tsx                 # React Bits Dock
│   │   │   └── Stepper.tsx
│   │   ├── projects/
│   │   │   ├── ProjectList.tsx
│   │   │   ├── ProjectCard.tsx
│   │   │   └── ProjectFilters.tsx
│   │   ├── workspace/
│   │   │   ├── WorkspaceLayout.tsx
│   │   │   ├── ContextPanel.tsx
│   │   │   └── steps/
│   │   │       ├── BriefStep.tsx
│   │   │       ├── ConceptStep.tsx
│   │   │       ├── ScreenplayCompare.tsx
│   │   │       ├── StoryboardViewer.tsx
│   │   │       ├── ProductionPackDashboard.tsx
│   │   │       └── ExportStep.tsx
│   │   ├── production/
│   │   │   ├── ProductionTile.tsx       # React Bits MagicBento
│   │   │   ├── BudgetEditor.tsx
│   │   │   └── ScheduleEditor.tsx
│   │   ├── shared/
│   │   │   ├── LoadingSkeleton.tsx
│   │   │   ├── StreamingText.tsx
│   │   │   ├── ProgressIndicator.tsx
│   │   │   ├── WarningBanner.tsx
│   │   │   └── EmptyState.tsx           # React Bits BlurText
│   │   └── ui/                          # shadcn/ui components
│   ├── contexts/
│   │   ├── ProjectContext.tsx
│   │   └── GenerationContext.tsx
│   ├── hooks/
│   │   ├── useProject.ts
│   │   ├── useGeneration.ts
│   │   └── useKeyboardNav.ts
│   ├── lib/
│   │   ├── api.ts                       # API client
│   │   ├── types.ts                     # TypeScript types
│   │   └── utils.ts
│   └── styles/
│       └── globals.css
├── public/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## Components and Interfaces

### Core Data Models

```typescript
// Project and workflow state
interface Project {
  id: string;
  name: string;
  client: string;
  status: ProjectStatus;
  createdAt: Date;
  updatedAt: Date;
  currentStep: WorkflowStep;
  brief?: Brief;
  concept?: Concept;
  screenplays?: Screenplay[];
  selectedScreenplay?: string; // screenplay ID
  storyboard?: Storyboard;
  productionPack?: ProductionPack;
  tags: string[];
  budgetBand: BudgetBand;
}

type ProjectStatus = 
  | 'draft' 
  | 'in_progress' 
  | 'needs_review' 
  | 'approved' 
  | 'archived';

type WorkflowStep = 
  | 'brief' 
  | 'concept' 
  | 'screenplays' 
  | 'select' 
  | 'storyboard' 
  | 'production' 
  | 'export';

type BudgetBand = 'low' | 'medium' | 'high' | 'premium';

// Brief
interface Brief {
  platform: string;
  duration: number; // seconds
  budget: number;
  location: string;
  constraints: string[];
  creativeDirection: string;
  brandMandatories: string[];
  targetAudience: string;
}

// Concept
interface Concept {
  id: string;
  title: string;
  description: string;
  keyMessage: string;
  visualStyle: string;
  generatedAt: Date;
  version: number;
}

// Screenplay
interface Screenplay {
  id: string;
  variant: 'A' | 'B';
  scenes: Scene[];
  totalDuration: number;
  scores: {
    clarity: number;
    feasibility: number;
    costRisk: number;
  };
  generatedAt: Date;
}

interface Scene {
  sceneNumber: number;
  duration: number;
  location: string;
  timeOfDay: string;
  description: string;
  dialogue: string[];
  action: string;
}

// Storyboard
interface Storyboard {
  id: string;
  scenes: StoryboardScene[];
  styleSettings: {
    styleLock: boolean;
    characterLock: boolean;
  };
  generatedAt: Date;
  version: number;
}

interface StoryboardScene {
  sceneNumber: number;
  imageUrl: string;
  visualDescription: string;
  cameraAngle: string;
  cameraMovement: string;
  onScreenText: string;
  audioNotes: string;
  duration: number;
}

// Production Pack
interface ProductionPack {
  id: string;
  documents: {
    shotlist: ProductionDocument;
    locations: ProductionDocument;
    budget: ProductionDocument;
    schedule: ProductionDocument;
    casting: ProductionDocument;
    propsWardrobe: ProductionDocument;
    legal: ProductionDocument;
    risk: ProductionDocument;
  };
  assumptions: Assumption[];
  changelog: ChangelogEntry[];
  generatedAt: Date;
  version: number;
}

interface ProductionDocument {
  type: DocumentType;
  status: DocumentStatus;
  content: any; // JSON structure varies by type
  warnings: Warning[];
  lastUpdated: Date;
}

type DocumentType = 
  | 'shotlist' 
  | 'locations' 
  | 'budget' 
  | 'schedule' 
  | 'casting' 
  | 'propsWardrobe' 
  | 'legal' 
  | 'risk';

type DocumentStatus = 'draft' | 'needs_review' | 'approved';

interface Warning {
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: 'legal' | 'brand' | 'location' | 'budget' | 'risk';
  message: string;
  affectedItems: string[];
}

interface Assumption {
  id: string;
  category: string;
  original: string;
  override?: string;
  editedBy?: string;
  editedAt?: Date;
}

interface ChangelogEntry {
  timestamp: Date;
  documentType: DocumentType;
  changes: string[];
  triggeredBy: 'regeneration' | 'user_edit';
}

// Generation state
interface GenerationState {
  isGenerating: boolean;
  step: WorkflowStep;
  progress: number; // 0-100
  estimatedTime: number; // seconds
  estimatedCost: number; // dollars
  startedAt?: Date;
  canCancel: boolean;
  error?: string;
  partialResults?: any;
}
```

### Key Component Interfaces

```typescript
// Navigation
interface DockProps {
  activeRoute: 'projects' | 'workspace' | 'assets' | 'settings';
  onNavigate: (route: string) => void;
}

interface StepperProps {
  currentStep: WorkflowStep;
  completedSteps: WorkflowStep[];
  lockedSteps: WorkflowStep[];
  onStepClick: (step: WorkflowStep) => void;
}

// Workspace
interface WorkspaceLayoutProps {
  project: Project;
  children: React.ReactNode;
}

interface ContextPanelProps {
  assumptions: Assumption[];
  constraints: string[];
  brandMandatories: string[];
  warnings: Warning[];
}

// Screenplay comparison
interface ScreenplayCompareProps {
  screenplayA: Screenplay;
  screenplayB: Screenplay;
  onSelect: (screenplayId: string) => void;
}

// Storyboard
interface StoryboardViewerProps {
  storyboard: Storyboard;
  onSceneRegenerate: (sceneNumber: number) => void;
  onStyleToggle: (setting: 'styleLock' | 'characterLock') => void;
  onDownload: (format: 'pdf' | 'png' | 'json') => void;
}

// Production Pack
interface ProductionPackDashboardProps {
  productionPack: ProductionPack;
  onDocumentOpen: (type: DocumentType) => void;
  onRegenerate: () => void;
}

interface ProductionTileProps {
  document: ProductionDocument;
  onClick: () => void;
}

// Generation
interface ProgressIndicatorProps {
  state: GenerationState;
  onCancel: () => void;
}

interface StreamingTextProps {
  text: string;
  isComplete: boolean;
}
```

### API Endpoints

```typescript
// Projects
GET    /api/projects                    // List all projects
POST   /api/projects                    // Create new project
GET    /api/projects/:id                // Get project details
PATCH  /api/projects/:id                // Update project
DELETE /api/projects/:id                // Delete project

// Brief
POST   /api/projects/:id/brief          // Submit brief
PATCH  /api/projects/:id/brief          // Update brief

// Generation
POST   /api/projects/:id/generate/concept        // Generate concept
POST   /api/projects/:id/generate/screenplays    // Generate screenplays
POST   /api/projects/:id/generate/storyboard     // Generate storyboard
POST   /api/projects/:id/generate/production     // Generate production pack
POST   /api/projects/:id/regenerate/scene/:num   // Regenerate single scene

// Selection
POST   /api/projects/:id/select/screenplay       // Select screenplay winner

// Streaming
GET    /api/stream/generation/:jobId    // SSE endpoint for generation progress

// Export
POST   /api/projects/:id/export         // Generate exports
GET    /api/projects/:id/exports/:id    // Download export file

// Production Pack
PATCH  /api/projects/:id/production/:docType     // Update production document
POST   /api/projects/:id/production/:docType/approve  // Approve document
```

## Data Models

### State Management Strategy

**Local State (React Context)**:
- Current project data
- Current workflow step
- UI state (modals, panels, filters)
- Generation progress

**Server State (React Query)**:
- Project list with caching
- Project details with automatic refetching
- Generation results with optimistic updates
- Export status

**Context Structure**:

```typescript
// ProjectContext
interface ProjectContextValue {
  project: Project | null;
  currentStep: WorkflowStep;
  isStepLocked: (step: WorkflowStep) => boolean;
  navigateToStep: (step: WorkflowStep) => void;
  updateProject: (updates: Partial<Project>) => Promise<void>;
}

// GenerationContext
interface GenerationContextValue {
  state: GenerationState;
  startGeneration: (step: WorkflowStep, params: any) => Promise<void>;
  cancelGeneration: () => void;
  subscribeToProgress: (jobId: string) => void;
}
```

### Database Schema (Backend)

The UI assumes the backend provides these data structures. The actual storage is handled by the Python backend.

```sql
-- Projects table
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  client VARCHAR(255),
  status VARCHAR(50),
  current_step VARCHAR(50),
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  brief JSONB,
  concept JSONB,
  screenplays JSONB,
  selected_screenplay UUID,
  storyboard JSONB,
  production_pack JSONB,
  tags TEXT[],
  budget_band VARCHAR(50)
);

-- Generation jobs table (for tracking async operations)
CREATE TABLE generation_jobs (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  step VARCHAR(50),
  status VARCHAR(50),
  progress INTEGER,
  estimated_time INTEGER,
  estimated_cost DECIMAL,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  error TEXT,
  result JSONB
);

-- Exports table
CREATE TABLE exports (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  format VARCHAR(50),
  file_url TEXT,
  created_at TIMESTAMP,
  created_by VARCHAR(255)
);
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Search and filter results match criteria

*For any* project list and any search/filter query, all displayed projects should match the filter criteria (status, client, date, budget band).

**Validates: Requirements 1.3**

### Property 2: Project metadata completeness

*For any* rendered project in the list view, the display should include status, client, date, and budget band fields.

**Validates: Requirements 1.4**

### Property 3: Brief validation rejects incomplete submissions

*For any* brief submission with missing required fields (platform, duration, budget, location, creative direction), the system should reject the submission and prevent progression.

**Validates: Requirements 2.3**

### Property 4: Brief API requests include all parameters

*For any* brief submission, the API request to the Backend_Pipeline should include all fields: platform, duration, budget, location constraints, creative direction, brand mandatories, and target audience.

**Validates: Requirements 2.4**

### Property 5: Brief data persistence round-trip

*For any* brief data, saving then loading should return equivalent data with all fields preserved.

**Validates: Requirements 2.5**

### Property 6: Constraint changes mark downstream steps

*For any* project with completed downstream steps (concept, screenplay, storyboard, production), modifying brief constraints should mark those steps as needing regeneration.

**Validates: Requirements 2.6**

### Property 7: Screenplay comparison displays all scores

*For any* pair of screenplay variants, the comparison view should display all three scoring chips: clarity, feasibility, and cost risk.

**Validates: Requirements 3.5**

### Property 8: HITL gate enforcement

*For any* project without a selected screenplay, the storyboard generation action should be disabled.

**Validates: Requirements 3.7**

### Property 9: Scene detail completeness

*For any* storyboard scene, the detail view should include visual description, camera angle, camera movement, on-screen text, and audio notes.

**Validates: Requirements 4.3**

### Property 10: Scene regeneration isolation

*For any* storyboard with multiple scenes, regenerating one scene should preserve all other scenes unchanged (only the target scene should have a new image URL and updated timestamp).

**Validates: Requirements 4.5**

### Property 11: Production tile information completeness

*For any* production document tile, the display should show status (Draft/Needs Review/Approved), last updated timestamp, and any warnings.

**Validates: Requirements 5.3**

### Property 12: Assumption override tracking

*For any* assumption edit, the system should create an override record with the original value, new value, editor, and timestamp.

**Validates: Requirements 5.5**

### Property 13: Regeneration produces changelog

*For any* production pack regeneration, the system should create a changelog entry listing what changed and when.

**Validates: Requirements 5.6**

### Property 14: Top risks visibility

*For any* production pack with risk warnings, the dashboard should display the top 3 highest-severity risks without requiring document navigation.

**Validates: Requirements 5.7**

### Property 15: Stepper highlights current step

*For any* project workspace, the stepper navigation should visually highlight the current active step.

**Validates: Requirements 6.2**

### Property 16: Step navigation respects locks

*For any* workflow step, clicking it in the stepper should navigate only if the step is unlocked; locked steps should not be navigable.

**Validates: Requirements 6.4**

### Property 17: Prerequisite-based step locking

*For any* project, a workflow step should be locked if its prerequisite steps are not completed (e.g., storyboard locked until screenplay selected).

**Validates: Requirements 6.5**

### Property 18: Locked step visual indication

*For any* locked workflow step, the UI should display a visual indicator (e.g., lock icon, disabled state, tooltip).

**Validates: Requirements 6.7**

### Property 19: Generation displays cost and time estimates

*For any* generation action (concept, screenplay, storyboard, production pack), the UI should display estimated time and cost before starting.

**Validates: Requirements 7.1**

### Property 20: Active generation shows progress

*For any* in-progress generation, the UI should display a progress indicator with cancellation option.

**Validates: Requirements 7.2**

### Property 21: Streaming results display incrementally

*For any* streaming generation response, partial results should be displayed as they arrive (not waiting for completion).

**Validates: Requirements 7.3**

### Property 22: Partial failure indication

*For any* generation that partially fails, the UI should indicate which components succeeded and which failed.

**Validates: Requirements 7.4**

### Property 23: Reduced motion support

*For any* animation, if the user's system has prefers-reduced-motion enabled, the animation should be disabled or significantly reduced.

**Validates: Requirements 8.5, 9.4**

### Property 24: Keyboard navigation completeness

*For any* interactive element in the Dock and Stepper components, it should be reachable and operable via keyboard (Tab, Enter, Arrow keys).

**Validates: Requirements 9.1**

### Property 25: Focus indicator visibility

*For any* interactive element, when focused via keyboard, a visible focus ring should be displayed.

**Validates: Requirements 9.2**

### Property 26: Color contrast compliance

*For any* text and background color combination, the contrast ratio should meet WCAG AA standards (4.5:1 for normal text, 3:1 for large text).

**Validates: Requirements 9.3**

### Property 27: ARIA label presence

*For any* interactive element without visible text (icons, buttons), appropriate ARIA labels should be present for screen readers.

**Validates: Requirements 9.5**

### Property 28: Warning display for detected issues

*For any* project with legal flags, risky claims, location permit risks, or missing brand mandatories, the system should display corresponding warnings in the UI.

**Validates: Requirements 10.1, 10.2, 10.3, 10.4**

### Property 29: Warning aggregation in dashboard

*For any* production pack with warnings across multiple documents, all warnings should be aggregated and visible in the Production Pack dashboard.

**Validates: Requirements 10.5**

### Property 30: Export generates files and links

*For any* export request (storyboard PDF/PNG/JSON, production pack PDF/spreadsheet), the system should generate files and provide download links.

**Validates: Requirements 11.4**

### Property 31: Export history tracking

*For any* completed export, the system should create a history record with timestamp, format, and user information.

**Validates: Requirements 11.5**

### Property 32: Generation request parameter completeness

*For any* generation API request, all required parameters from the brief and user selections should be included in the request payload.

**Validates: Requirements 12.2**

### Property 33: API response parsing

*For any* valid API response from the Backend_Pipeline, the system should successfully parse the structured data and display it without errors.

**Validates: Requirements 12.3**

### Property 34: Error message user-friendliness

*For any* error response from the Backend_Pipeline, the system should display a user-friendly error message (not raw error codes or stack traces).

**Validates: Requirements 12.4**

### Property 35: Streaming response handling

*For any* streaming API response, the system should process and display updates as they arrive in real-time.

**Validates: Requirements 12.5**

### Property 36: Authentication persistence

*For any* sequence of API requests within a session, authentication tokens should be maintained and included in all requests.

**Validates: Requirements 12.6**

## Error Handling

### Error Categories

**1. Network Errors**
- Connection failures to Backend_Pipeline
- Timeout errors during long-running generation
- SSE connection drops during streaming

**Handling Strategy**:
- Display user-friendly error messages with retry options
- Implement exponential backoff for retries
- Preserve user input and state during errors
- Show offline indicator when backend is unreachable

**2. Validation Errors**
- Incomplete brief submissions
- Invalid input formats
- Missing required fields

**Handling Strategy**:
- Inline validation with immediate feedback
- Clear error messages next to problematic fields
- Prevent submission until validation passes
- Preserve valid fields when showing errors

**3. Generation Errors**
- Backend pipeline failures
- Partial generation failures (some agents succeed, others fail)
- Content policy violations
- Resource exhaustion (quota limits, rate limits)

**Handling Strategy**:
- Show which specific generation step failed
- Preserve successful partial results
- Offer retry with adjusted parameters
- Display cost/quota information when relevant
- Log errors for debugging

**4. State Errors**
- Attempting locked operations
- Invalid workflow transitions
- Concurrent modification conflicts

**Handling Strategy**:
- Prevent invalid actions through UI disabling
- Show clear explanations for why actions are locked
- Implement optimistic locking for concurrent edits
- Refresh state when conflicts detected

**5. Export Errors**
- File generation failures
- Storage errors
- Format conversion errors

**Handling Strategy**:
- Show specific error for failed export type
- Offer alternative formats
- Retry mechanism with progress indication
- Fallback to simpler export formats

### Error UI Components

```typescript
interface ErrorBoundaryProps {
  fallback: React.ReactNode;
  onReset: () => void;
}

interface ErrorMessageProps {
  severity: 'error' | 'warning' | 'info';
  message: string;
  details?: string;
  actions?: ErrorAction[];
}

interface ErrorAction {
  label: string;
  onClick: () => void;
  variant: 'primary' | 'secondary';
}
```

### Error Recovery Patterns

**Graceful Degradation**:
- If streaming fails, fall back to polling
- If image generation fails, show placeholder with retry
- If cost estimation fails, show generation without estimate

**State Preservation**:
- Save form data to localStorage during errors
- Preserve generation progress when possible
- Cache successful partial results

**User Communication**:
- Clear, non-technical error messages
- Actionable next steps
- Contact support option for persistent errors
- Error tracking IDs for support reference

## Testing Strategy

### Dual Testing Approach

The testing strategy employs both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests**: Focus on specific examples, edge cases, and integration points
- Component rendering with specific props
- User interaction flows (click, type, navigate)
- API integration with mocked responses
- Error boundary behavior
- Accessibility features (keyboard nav, ARIA labels)

**Property-Based Tests**: Verify universal properties across all inputs
- Data validation and filtering logic
- State management invariants
- UI consistency across different data shapes
- Accessibility compliance across all components

Together, these approaches provide comprehensive coverage: unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across the input space.

### Testing Framework Setup

**Framework**: Vitest + React Testing Library + fast-check (property-based testing)

**Configuration**:
```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['**/*.stories.tsx', '**/*.test.tsx']
    }
  }
});
```

**Property Test Configuration**:
- Minimum 100 iterations per property test
- Each property test tagged with: `// Feature: virtual-ad-agency-ui, Property N: [property text]`
- Custom generators for domain objects (Project, Brief, Screenplay, etc.)

### Test Organization

```
src/
├── components/
│   ├── projects/
│   │   ├── ProjectList.tsx
│   │   ├── ProjectList.test.tsx          # Unit tests
│   │   └── ProjectList.properties.test.tsx  # Property tests
│   ├── workspace/
│   │   └── steps/
│   │       ├── ScreenplayCompare.tsx
│   │       ├── ScreenplayCompare.test.tsx
│   │       └── ScreenplayCompare.properties.test.tsx
├── test/
│   ├── setup.ts
│   ├── generators.ts                     # fast-check generators
│   ├── fixtures.ts                       # Test data fixtures
│   └── utils.ts                          # Test utilities
```

### Property Test Examples

```typescript
// Feature: virtual-ad-agency-ui, Property 1: Search and filter results match criteria
describe('ProjectList filtering', () => {
  it('should only show projects matching filter criteria', () => {
    fc.assert(
      fc.property(
        fc.array(projectGenerator()),
        fc.record({
          status: fc.option(fc.constantFrom('draft', 'in_progress', 'approved')),
          client: fc.option(fc.string()),
          budgetBand: fc.option(fc.constantFrom('low', 'medium', 'high'))
        }),
        (projects, filters) => {
          const filtered = filterProjects(projects, filters);
          return filtered.every(project => 
            matchesFilter(project, filters)
          );
        }
      ),
      { numRuns: 100 }
    );
  });
});

// Feature: virtual-ad-agency-ui, Property 5: Brief data persistence round-trip
describe('Brief persistence', () => {
  it('should preserve all fields through save/load cycle', () => {
    fc.assert(
      fc.property(
        briefGenerator(),
        async (brief) => {
          const saved = await saveBrief(brief);
          const loaded = await loadBrief(saved.id);
          return deepEqual(brief, loaded);
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

### Unit Test Examples

```typescript
describe('ProjectList', () => {
  it('should display empty state when no projects exist', () => {
    render(<ProjectList projects={[]} />);
    expect(screen.getByText(/no projects yet/i)).toBeInTheDocument();
  });

  it('should navigate to brief step when clicking New Project', async () => {
    const user = userEvent.setup();
    render(<ProjectList projects={[]} />);
    await user.click(screen.getByRole('button', { name: /new project/i }));
    expect(mockRouter.push).toHaveBeenCalledWith('/projects/new/brief');
  });
});

describe('ScreenplayCompare', () => {
  it('should display both screenplay variants', () => {
    const { screenplayA, screenplayB } = createMockScreenplays();
    render(<ScreenplayCompare screenplayA={screenplayA} screenplayB={screenplayB} />);
    expect(screen.getByText(/variant a/i)).toBeInTheDocument();
    expect(screen.getByText(/variant b/i)).toBeInTheDocument();
  });
});
```

### Accessibility Testing

```typescript
describe('Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<ProjectList projects={mockProjects} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should support keyboard navigation in stepper', async () => {
    const user = userEvent.setup();
    render(<Stepper currentStep="brief" />);
    await user.tab();
    expect(screen.getByRole('button', { name: /brief/i })).toHaveFocus();
    await user.keyboard('{ArrowRight}');
    expect(screen.getByRole('button', { name: /concept/i })).toHaveFocus();
  });
});
```

### Integration Testing

```typescript
describe('End-to-end workflow', () => {
  it('should complete full project creation flow', async () => {
    const user = userEvent.setup();
    
    // Start new project
    render(<App />);
    await user.click(screen.getByRole('button', { name: /new project/i }));
    
    // Fill brief
    await user.type(screen.getByLabelText(/platform/i), 'Instagram');
    await user.type(screen.getByLabelText(/duration/i), '30');
    await user.click(screen.getByRole('button', { name: /generate concept/i }));
    
    // Wait for concept
    await waitFor(() => {
      expect(screen.getByText(/concept generated/i)).toBeInTheDocument();
    });
    
    // Continue through workflow...
  });
});
```

### Test Coverage Goals

- **Unit Test Coverage**: 80%+ for component logic
- **Property Test Coverage**: All data transformation and validation functions
- **Integration Test Coverage**: All critical user flows
- **Accessibility Test Coverage**: All interactive components
- **Visual Regression**: Key screens and components (using Chromatic or Percy)

### Continuous Testing

- Run unit tests on every commit (pre-commit hook)
- Run full test suite in CI/CD pipeline
- Property tests run with 100 iterations in CI, 1000 iterations nightly
- Accessibility tests run on every PR
- Visual regression tests run on UI changes
