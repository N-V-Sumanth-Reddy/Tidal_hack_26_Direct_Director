// Core domain types for the virtual ad agency workspace

// ============================================================================
// Enums and Type Unions
// ============================================================================

export type ProjectStatus = 
  | 'draft' 
  | 'in_progress' 
  | 'needs_review' 
  | 'approved' 
  | 'archived';

export type WorkflowStep = 
  | 'brief' 
  | 'concept' 
  | 'screenplays' 
  | 'select' 
  | 'storyboard' 
  | 'production' 
  | 'export';

export type BudgetBand = 'low' | 'medium' | 'high' | 'premium';

export type DocumentType = 
  | 'shotlist' 
  | 'locations' 
  | 'budget' 
  | 'schedule' 
  | 'casting' 
  | 'propsWardrobe' 
  | 'legal' 
  | 'risk';

export type DocumentStatus = 'draft' | 'needs_review' | 'approved';

export type WarningSeverity = 'low' | 'medium' | 'high' | 'critical';

export type WarningCategory = 'legal' | 'brand' | 'location' | 'budget' | 'risk';

// ============================================================================
// Project and Workflow
// ============================================================================

export interface Project {
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

// ============================================================================
// Brief
// ============================================================================

export interface Brief {
  platform: string;
  duration: number; // seconds
  budget: number;
  location: string;
  constraints: string[];
  creativeDirection: string;
  brandMandatories: string[];
  targetAudience: string;
}

// ============================================================================
// Concept
// ============================================================================

export interface Concept {
  id: string;
  title: string;
  description: string;
  keyMessage: string;
  visualStyle: string;
  generatedAt: Date;
  version: number;
}

// ============================================================================
// Screenplay
// ============================================================================

export interface Screenplay {
  id: string;
  variant: string; // "A (Rajamouli Style)" or "B (Shankar Style)"
  scenes: Scene[];
  totalDuration: number;
  scores: {
    clarity: number;
    feasibility: number;
    costRisk: number;
  };
  generatedAt: Date;
}

export interface Scene {
  sceneNumber: number;
  duration: number;
  description: string;
}

// ============================================================================
// Storyboard
// ============================================================================

export interface Storyboard {
  id: string;
  scenes: StoryboardScene[];
  styleSettings?: {
    styleLock: boolean;
    characterLock: boolean;
  };
  generatedAt: Date;
  version?: number;
}

export interface StoryboardScene {
  id?: string;
  sceneNumber: number;
  imageUrl: string | null;
  description: string;
  cameraAngle: string;
  cameraMovement?: string;
  onScreenText?: string;
  audioNotes?: string;
  dialogue?: string | null;
  notes?: string;
  duration: number;
}

// ============================================================================
// Production Pack
// ============================================================================

export interface ProductionPack {
  id: string;
  generatedAt: Date;
  scenePlan?: {
    scenes: Array<{
      scene_id: string;
      duration_sec: number;
      location_type: string; // "INT" or "EXT"
      time_of_day: string; // "DAY" or "NIGHT"
      location_description: string;
      cast_count: number;
      props: string[];
      wardrobe: string[];
      sfx_vfx?: string[];
      dialogue_vo?: string;
      on_screen_text?: string;
    }>;
    shots: Array<{
      shot_id: string;
      scene_id: string;
      shot_type: string; // "WIDE", "MEDIUM", "CLOSE-UP", etc.
      camera_movement: string; // "STATIC", "PAN", "DOLLY", etc.
      duration_sec: number;
      description: string;
    }>;
  };
  budget?: {
    total_min: number;
    total_max: number;
    line_items: Array<{
      category: string;
      item: string;
      quantity: number;
      unit_cost: number;
      total_cost: number;
    }>;
    assumptions?: string[];
    cost_drivers?: string[];
  };
  schedule?: {
    total_shoot_days: number;
    days: Array<{
      day: number;
      location: string;
      scenes: string[]; // scene IDs
      setup_time_hours?: number;
      shoot_time_hours?: number;
    }>;
    company_moves?: Array<{
      from: string;
      to: string;
      estimated_time_hours: number;
    }>;
  };
  locations?: Array<{
    name: string;
    type: string; // "INT" or "EXT"
    requirements: string;
    alternates?: string[];
    permits_required?: string[];
  }>;
  crew?: Array<{
    role: string;
    responsibilities: string;
    required?: boolean;
  }>;
  equipment?: Array<{
    item: string;
    quantity: number;
    required?: boolean;
  }>;
  legal?: Array<{
    item: string;
    description: string;
    quantity?: number;
    high_risk?: boolean;
  }>;
  risks?: Array<{
    risk: string;
    likelihood: string; // "LOW", "MEDIUM", "HIGH"
    impact: string; // "LOW", "MEDIUM", "HIGH"
    mitigation: string;
  }>;
  error?: string; // For debugging if generation partially failed
}

export interface ProductionDocument {
  type: DocumentType;
  status: DocumentStatus;
  content: any; // JSON structure varies by type
  warnings: Warning[];
  lastUpdated: Date;
}

export interface Warning {
  severity: WarningSeverity;
  category: WarningCategory;
  message: string;
  affectedItems: string[];
}

export interface Assumption {
  id: string;
  category: string;
  original: string;
  override?: string;
  editedBy?: string;
  editedAt?: Date;
}

export interface ChangelogEntry {
  timestamp: Date;
  documentType: DocumentType;
  changes: string[];
  triggeredBy: 'regeneration' | 'user_edit';
}

// ============================================================================
// Generation State
// ============================================================================

export interface GenerationState {
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

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface CreateProjectRequest {
  name: string;
  client: string;
  tags?: string[];
  budgetBand: BudgetBand;
}

export interface UpdateProjectRequest {
  name?: string;
  client?: string;
  status?: ProjectStatus;
  currentStep?: WorkflowStep;
  tags?: string[];
  budgetBand?: BudgetBand;
}

export interface SubmitBriefRequest {
  brief: Brief;
}

export interface GenerateConceptRequest {
  projectId: string;
  brief: Brief;
}

export interface GenerateScreenplaysRequest {
  projectId: string;
  conceptId: string;
}

export interface SelectScreenplayRequest {
  projectId: string;
  screenplayId: string;
}

export interface GenerateStoryboardRequest {
  projectId: string;
  screenplayId: string;
  styleSettings?: {
    styleLock?: boolean;
    characterLock?: boolean;
  };
}

export interface RegenerateSceneRequest {
  projectId: string;
  storyboardId: string;
  sceneNumber: number;
}

export interface GenerateProductionPackRequest {
  projectId: string;
  storyboardId: string;
}

export interface UpdateProductionDocumentRequest {
  projectId: string;
  documentType: DocumentType;
  content: any;
}

export interface ApproveDocumentRequest {
  projectId: string;
  documentType: DocumentType;
}

export interface ExportRequest {
  projectId: string;
  format: 'pdf' | 'png' | 'json' | 'spreadsheet';
  target: 'storyboard' | 'production_pack';
}

export interface ExportResponse {
  id: string;
  fileUrl: string;
  format: string;
  createdAt: Date;
}

// ============================================================================
// Filter and Search Types
// ============================================================================

export interface ProjectFilters {
  status?: ProjectStatus;
  client?: string;
  budgetBand?: BudgetBand;
  dateFrom?: Date;
  dateTo?: Date;
  tags?: string[];
  search?: string;
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface DockProps {
  activeRoute: 'projects' | 'workspace' | 'assets' | 'settings';
  onNavigate: (route: string) => void;
}

export interface StepperProps {
  currentStep: WorkflowStep;
  completedSteps: WorkflowStep[];
  lockedSteps: WorkflowStep[];
  onStepClick: (step: WorkflowStep) => void;
}

export interface WorkspaceLayoutProps {
  project: Project;
  children: React.ReactNode;
}

export interface ContextPanelProps {
  assumptions: Assumption[];
  constraints: string[];
  brandMandatories: string[];
  warnings: Warning[];
}

export interface ScreenplayCompareProps {
  screenplayA: Screenplay;
  screenplayB: Screenplay;
  onSelect: (screenplayId: string) => void;
}

export interface StoryboardViewerProps {
  storyboard: Storyboard;
  onSceneRegenerate: (sceneNumber: number) => void;
  onStyleToggle: (setting: 'styleLock' | 'characterLock') => void;
  onDownload: (format: 'pdf' | 'png' | 'json') => void;
}

export interface ProductionPackDashboardProps {
  productionPack: ProductionPack;
  onDocumentOpen: (type: DocumentType) => void;
  onRegenerate: () => void;
}

export interface ProductionTileProps {
  document: ProductionDocument;
  onClick: () => void;
}

export interface ProgressIndicatorProps {
  state: GenerationState;
  onCancel: () => void;
}

export interface StreamingTextProps {
  text: string;
  isComplete: boolean;
}
