# Virtual Ad Agency Workspace UI

A Next.js application providing an intuitive, step-based interface for managing AI-powered ad production workflows from brief intake through creative generation, storyboard development, and production planning.

## 🎯 Overview

This application guides users through a structured pipeline:
1. **Brief Intake** - Define project requirements
2. **Concept Generation** - AI-generated creative concepts
3. **Screenplay Variants** - Two screenplay options with scoring
4. **HITL Selection** - Human-in-the-loop screenplay selection
5. **Storyboard Generation** - Visual scene-by-scene storyboards
6. **Production Pack** - Comprehensive production documents (budget, schedule, locations, legal, risk)
7. **Export** - Download deliverables in multiple formats

## 🏗️ Architecture

### Tech Stack
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS v4
- **Components**: shadcn/ui + React Bits
- **State**: React Context + React Query
- **Testing**: Vitest + React Testing Library + fast-check
- **Backend**: FastAPI (Python) - integrates with existing pipelines

### Project Structure
```
virtual-ad-agency-ui/
├── app/                    # Next.js app router
│   ├── projects/          # Project list and workspace
│   ├── providers.tsx      # Global providers
│   └── layout.tsx         # Root layout
├── components/
│   ├── shared/            # Reusable UI components
│   ├── navigation/        # Dock, Stepper
│   ├── projects/          # Project management
│   └── workspace/         # Workflow steps
├── contexts/              # React Context providers
│   ├── ProjectContext.tsx
│   └── GenerationContext.tsx
├── hooks/                 # Custom React hooks
│   ├── useProjects.ts
│   └── useGeneration.ts
├── lib/                   # Core utilities
│   ├── api.ts            # REST API client
│   ├── sse-client.ts     # Server-Sent Events
│   ├── types.ts          # TypeScript definitions
│   └── utils.ts          # Helper functions
└── test/                  # Test utilities
    ├── generators.ts      # Property-based test generators
    ├── fixtures.ts        # Mock data
    └── setup.ts           # Test configuration
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+ (for backend)
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API URL

# Run development server
npm run dev

# Run tests
npm test

# Run tests with UI
npm run test:ui

# Build for production
npm run build
```

### Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📡 Backend Integration

The UI communicates with a FastAPI backend that wraps your existing Python pipelines:

### Expected API Endpoints

```
GET    /api/projects                    # List projects
POST   /api/projects                    # Create project
GET    /api/projects/:id                # Get project
PATCH  /api/projects/:id                # Update project
DELETE /api/projects/:id                # Delete project

POST   /api/projects/:id/brief          # Submit brief
POST   /api/projects/:id/generate/concept
POST   /api/projects/:id/generate/screenplays
POST   /api/projects/:id/generate/storyboard
POST   /api/projects/:id/generate/production

POST   /api/projects/:id/select/screenplay
POST   /api/projects/:id/regenerate/scene/:num

GET    /api/stream/generation/:jobId    # SSE for progress
POST   /api/jobs/:jobId/cancel          # Cancel generation

POST   /api/projects/:id/export         # Generate exports
GET    /api/projects/:id/exports/:id    # Download export
```

### Backend Setup (FastAPI)

Create a FastAPI backend that integrates with your existing pipelines:

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
sys.path.append('../')  # Add parent directory to path

from ad_video_pipeline import AdVideoPipeline
from ad_production_pipeline import ProductionPipeline

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipelines
video_pipeline = AdVideoPipeline()
production_pipeline = ProductionPipeline()

@app.post("/api/projects/{project_id}/generate/concept")
async def generate_concept(project_id: str, brief: dict):
    # Call your existing pipeline
    result = video_pipeline.generate_concept(brief)
    return {"jobId": "...", "estimatedTime": 60, "estimatedCost": 0.50}

# ... more endpoints
```

## 🎨 Key Features

### State Management
- **ProjectContext**: Manages current project, workflow step, and navigation
- **GenerationContext**: Handles generation state, progress, and SSE subscriptions
- **React Query**: Server state with caching, optimistic updates, and automatic refetching

### Real-time Updates
- Server-Sent Events (SSE) for generation progress
- Automatic reconnection with exponential backoff
- Streaming text display with typing animation

### Workflow Step Locking
Steps are automatically locked based on prerequisites:
- Concept requires Brief
- Screenplays require Concept
- Storyboard requires Screenplay selection (HITL gate)
- Production Pack requires Storyboard
- Export requires Production Pack

### Error Handling
- User-friendly error messages
- Automatic retry with exponential backoff
- Graceful degradation (SSE → polling fallback)
- State preservation during errors

## 🧪 Testing

### Test Strategy
- **Unit Tests**: Component rendering, user interactions, API integration
- **Property-Based Tests**: Universal properties across all inputs (using fast-check)
- **Accessibility Tests**: WCAG AA compliance (using axe-core)

### Running Tests

```bash
# Run all tests
npm test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- LoadingSkeleton.test.tsx
```

### Test Generators

Property-based test generators are available for all domain objects:

```typescript
import { projectGenerator, briefGenerator } from '@/test/generators';
import * as fc from 'fast-check';

fc.assert(
  fc.property(projectGenerator(), (project) => {
    // Test property holds for all generated projects
    expect(project.id).toBeDefined();
  })
);
```

## 📦 Components

### Shared Components
- **LoadingSkeleton**: Animated loading states (text, card, image, circle, button)
- **ProgressIndicator**: Generation progress with time/cost estimates
- **StreamingText**: Character-by-character text reveal
- **WarningBanner**: Severity-based warnings (low, medium, high, critical)
- **EmptyState**: Placeholder states with actions

### Navigation
- **Dock**: Primary navigation (React Bits)
- **Stepper**: Workflow step navigation with locking

### Workflow Steps
- **BriefStep**: Form for project requirements
- **ConceptStep**: Display generated concept
- **ScreenplayCompare**: Side-by-side screenplay comparison
- **StoryboardViewer**: Scene list with thumbnails and details
- **ProductionPackDashboard**: Production document tiles
- **ExportStep**: Download options and history

## 🎯 Roadmap

### Phase 1: Foundation ✅
- [x] Project setup
- [x] Type system
- [x] API layer
- [x] State management
- [x] Shared components

### Phase 2: Core UI (In Progress)
- [ ] Navigation components
- [ ] Project list and management
- [ ] Workflow step components
- [ ] Production pack features

### Phase 3: Polish
- [ ] Accessibility features
- [ ] Reduced motion support
- [ ] Error boundaries
- [ ] Performance optimization

### Phase 4: Backend
- [ ] FastAPI backend
- [ ] Pipeline integration
- [ ] Database setup
- [ ] Authentication

## 📝 License

MIT

## 🤝 Contributing

This is a private project. For questions or issues, contact the development team.

## 📞 Support

For technical support or questions about the application, please refer to the internal documentation or contact the development team.
