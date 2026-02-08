# Requirements Document

## Introduction

This document specifies the requirements for a virtual ad agency workspace UI application. The system provides a React-based interface for managing ad production pipelines, guiding users through project creation, creative development, storyboard generation, and production pack creation. The UI integrates with existing Python backend services that handle AI-powered content generation.

## Glossary

- **System**: The virtual ad agency workspace UI application
- **User**: A person using the application to create and manage ad production projects
- **Project**: A container for a single ad production workflow from brief to final deliverables
- **Brief**: Initial project requirements including platform, duration, budget, and creative direction
- **Concept**: High-level creative idea generated from the brief
- **Screenplay**: Detailed scene-by-scene script (system generates 2 variants)
- **Storyboard**: Visual representation of the screenplay with scene images and details
- **Production_Pack**: Collection of production documents (shotlist, budget, schedule, locations, legal, risk)
- **HITL**: Human-in-the-loop decision point requiring user approval
- **Workspace**: Per-project interface showing the step-based workflow
- **Step**: A phase in the workflow (Brief, Concept, Screenplays, Select, Storyboard, Production, Export)
- **Regeneration**: Re-running generation for a step while preserving approved upstream decisions
- **Backend_Pipeline**: Existing Python services (ad_video_pipeline.py, ad_production_pipeline.py)
- **React_Bits**: Animation component library for UI motion and interactions
- **Dock**: Primary navigation component from React Bits
- **MagicBento**: Dashboard tile component from React Bits
- **Stepper**: Step-based navigation component showing workflow progress

## Requirements

### Requirement 1: Project Management

**User Story:** As a user, I want to create and manage multiple ad production projects, so that I can organize my work and track progress across different campaigns.

#### Acceptance Criteria

1. WHEN a user navigates to the Projects page, THE System SHALL display a list of all projects with search and filter capabilities
2. WHEN a user clicks "New Project", THE System SHALL initiate the project creation flow starting with brief intake
3. WHEN a user searches or filters projects, THE System SHALL update the display to show only matching projects
4. WHEN viewing the project list, THE System SHALL display project metadata including status, client, date, and budget band
5. WHEN the project list is empty, THE System SHALL display an animated empty state with guidance explaining project structure
6. THE System SHALL support both table and grid view toggles for the project list

### Requirement 2: Brief Intake

**User Story:** As a user, I want to enter project requirements through a structured brief form, so that the system can generate appropriate creative content.

#### Acceptance Criteria

1. WHEN a user creates a new project, THE System SHALL display a brief intake form as the first step
2. THE System SHALL collect platform, duration, budget, location constraints, and creative direction in the brief form
3. WHEN a user submits a brief, THE System SHALL validate all required fields before proceeding
4. WHEN a brief is submitted, THE System SHALL send the brief data to the Backend_Pipeline for processing
5. THE System SHALL persist brief data and allow users to edit it before generation starts
6. WHEN brief constraints are modified after downstream steps are complete, THE System SHALL mark affected downstream steps for regeneration

### Requirement 3: Creative Generation and Selection

**User Story:** As a user, I want to generate creative concepts and screenplay variants, so that I can choose the best creative direction for my ad.

#### Acceptance Criteria

1. WHEN a brief is approved, THE System SHALL trigger concept generation via the Backend_Pipeline
2. WHEN concept generation completes, THE System SHALL display the generated concept and enable screenplay generation
3. WHEN screenplay generation is triggered, THE System SHALL request 2 screenplay variants from the Backend_Pipeline
4. WHEN screenplay variants are generated, THE System SHALL display a two-column comparison view with diff highlights
5. WHEN comparing screenplays, THE System SHALL display scoring chips for clarity, feasibility, and cost risk
6. WHEN a user selects a screenplay winner, THE System SHALL lock that selection and enable storyboard generation
7. THE System SHALL prevent storyboard generation until a screenplay is selected (HITL gate)

### Requirement 4: Storyboard Viewing and Management

**User Story:** As a user, I want to view and manage generated storyboards with scene-level details, so that I can review visual storytelling and make adjustments.

#### Acceptance Criteria

1. WHEN a screenplay is selected, THE System SHALL trigger storyboard generation via the Backend_Pipeline
2. WHEN storyboard generation completes, THE System SHALL display a scene list with thumbnail images
3. WHEN a user clicks a scene thumbnail, THE System SHALL display detailed scene information including visual description, camera notes, on-screen text, and audio notes
4. THE System SHALL provide consistency controls for style lock and character lock across scenes
5. WHEN a user requests scene regeneration, THE System SHALL regenerate only that scene image while preserving other scenes
6. THE System SHALL provide download options for storyboard PDF, PNG pack, and structured JSON

### Requirement 5: Production Pack Generation and Management

**User Story:** As a user, I want to generate and manage production documents, so that I can plan the actual ad production with detailed logistics and budgets.

#### Acceptance Criteria

1. WHEN a storyboard is approved, THE System SHALL trigger production pack generation via the Backend_Pipeline
2. WHEN production pack generation completes, THE System SHALL display a dashboard with tiles for Shotlist, Locations, Budget, Schedule, Casting, Props/Wardrobe, Legal, and Risk
3. WHEN displaying production pack tiles, THE System SHALL show status (Draft/Needs Review/Approved), last updated timestamp, and key warnings for each document
4. THE System SHALL provide spreadsheet-like editors for Budget and Schedule documents
5. WHEN a user edits assumptions, THE System SHALL track edits as overrides and display them in an assumptions panel
6. WHEN production pack regeneration occurs, THE System SHALL display a changelog showing what changed
7. THE System SHALL display top 3 risks on the dashboard without requiring users to open documents

### Requirement 6: Workspace Navigation and State Management

**User Story:** As a user, I want to navigate through the workflow steps and see my progress, so that I understand where I am in the process and what comes next.

#### Acceptance Criteria

1. WHEN a user opens a project workspace, THE System SHALL display a stepper navigation showing all workflow steps (Brief, Concept, Screenplays, Select, Storyboard, Production, Export)
2. THE System SHALL highlight the current active step in the stepper navigation
3. THE System SHALL display a context panel showing assumptions, constraints, brand mandatories, and warnings
4. WHEN a user clicks a step in the stepper, THE System SHALL navigate to that step if it is unlocked
5. THE System SHALL lock downstream steps until their prerequisites are completed
6. THE System SHALL display version history for each step with regeneration controls
7. WHEN a step is approved and locked, THE System SHALL visually indicate the locked state

### Requirement 7: Generation Progress and Cost Transparency

**User Story:** As a user, I want to see progress and cost estimates for generation operations, so that I can make informed decisions and cancel if needed.

#### Acceptance Criteria

1. WHEN a user triggers any generation action, THE System SHALL display estimated time and cost before starting
2. WHILE generation is in progress, THE System SHALL display cancellable progress indicators
3. WHEN generation is streaming results, THE System SHALL display partial results as they arrive
4. IF generation partially fails, THE System SHALL indicate which agents completed and which failed
5. THE System SHALL display loading skeletons while waiting for generation to start
6. WHEN generation completes, THE System SHALL update the UI to show the completed state

### Requirement 8: React Bits Integration for Enhanced UX

**User Story:** As a user, I want smooth, meaningful animations that communicate system state, so that I can understand what the system is doing without reading text.

#### Acceptance Criteria

1. THE System SHALL use the Dock component from React Bits for primary navigation (Projects/Workspace/Assets/Settings)
2. THE System SHALL use the MagicBento component from React Bits for Production Pack dashboard tiles
3. THE System SHALL use the LogoLoop component from React Bits on marketing/landing pages
4. THE System SHALL use the BlurText component from React Bits for empty states and onboarding hints
5. WHEN animations are displayed, THE System SHALL respect the prefers-reduced-motion accessibility preference
6. THE System SHALL use motion to communicate states: generating, queued, needs review, approved, blocked

### Requirement 9: Accessibility and Keyboard Navigation

**User Story:** As a user with accessibility needs, I want to navigate and use the application with keyboard and screen readers, so that I can work effectively regardless of my abilities.

#### Acceptance Criteria

1. THE System SHALL support full keyboard navigation for Dock navigation and stepper components
2. THE System SHALL display visible focus rings on all interactive elements
3. THE System SHALL maintain readable contrast ratios meeting WCAG AA standards
4. WHEN a user enables prefers-reduced-motion, THE System SHALL disable or reduce all animations
5. THE System SHALL provide appropriate ARIA labels and semantic HTML for screen readers

### Requirement 10: Warnings and Compliance Indicators

**User Story:** As a user, I want to see warnings and compliance issues prominently, so that I can address legal, brand, and production risks before finalizing.

#### Acceptance Criteria

1. WHEN legal flags are detected, THE System SHALL display compliance banners with specific issues
2. WHEN risky claims are identified, THE System SHALL highlight them with warning indicators
3. WHEN location permit risks are detected, THE System SHALL display location-specific warnings
4. WHEN brand mandatories are missing, THE System SHALL display prominent warnings in the context panel
5. THE System SHALL aggregate warnings and display them in the Production Pack dashboard

### Requirement 11: Export and Deliverables

**User Story:** As a user, I want to export final deliverables in multiple formats, so that I can share them with stakeholders and production teams.

#### Acceptance Criteria

1. WHEN a production pack is approved, THE System SHALL enable the Export step
2. THE System SHALL provide export options for storyboard PDF, storyboard PNG pack, and structured JSON
3. THE System SHALL provide export options for production pack documents in PDF and spreadsheet formats
4. WHEN a user triggers an export, THE System SHALL generate the files and provide download links
5. THE System SHALL track export history with timestamps and user information

### Requirement 12: Backend Integration

**User Story:** As a developer, I want the UI to integrate seamlessly with existing Python backend services, so that the system leverages existing AI generation capabilities.

#### Acceptance Criteria

1. THE System SHALL communicate with the Backend_Pipeline via HTTP API endpoints
2. WHEN sending generation requests, THE System SHALL include all required parameters from the brief and user selections
3. WHEN receiving generation results, THE System SHALL parse and display the structured data correctly
4. IF the Backend_Pipeline returns errors, THE System SHALL display user-friendly error messages
5. THE System SHALL handle streaming responses from the Backend_Pipeline for real-time updates
6. THE System SHALL maintain session state and authentication tokens for Backend_Pipeline requests
