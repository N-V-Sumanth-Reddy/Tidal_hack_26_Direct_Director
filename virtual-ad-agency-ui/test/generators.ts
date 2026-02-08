import * as fc from 'fast-check';
import type {
  Project,
  Brief,
  Concept,
  Screenplay,
  Scene,
  Storyboard,
  StoryboardScene,
  ProductionPack,
  ProductionDocument,
  Warning,
  Assumption,
  ChangelogEntry,
  ProjectStatus,
  WorkflowStep,
  BudgetBand,
  DocumentType,
  DocumentStatus,
} from '@/lib/types';

// ============================================================================
// Enum Generators
// ============================================================================

export const projectStatusGenerator = () =>
  fc.constantFrom<ProjectStatus>(
    'draft',
    'in_progress',
    'needs_review',
    'approved',
    'archived'
  );

export const workflowStepGenerator = () =>
  fc.constantFrom<WorkflowStep>(
    'brief',
    'concept',
    'screenplays',
    'select',
    'storyboard',
    'production',
    'export'
  );

export const budgetBandGenerator = () =>
  fc.constantFrom<BudgetBand>('low', 'medium', 'high', 'premium');

export const documentTypeGenerator = () =>
  fc.constantFrom<DocumentType>(
    'shotlist',
    'locations',
    'budget',
    'schedule',
    'casting',
    'propsWardrobe',
    'legal',
    'risk'
  );

export const documentStatusGenerator = () =>
  fc.constantFrom<DocumentStatus>('draft', 'needs_review', 'approved');

// ============================================================================
// Domain Object Generators
// ============================================================================

export const briefGenerator = (): fc.Arbitrary<Brief> =>
  fc.record({
    platform: fc.constantFrom('YouTube', 'Instagram', 'TikTok', 'TV', 'Web'),
    duration: fc.integer({ min: 15, max: 120 }),
    budget: fc.integer({ min: 1000, max: 1000000 }),
    location: fc.string({ minLength: 3, maxLength: 50 }),
    constraints: fc.array(fc.string({ minLength: 5, maxLength: 100 }), {
      maxLength: 5,
    }),
    creativeDirection: fc.string({ minLength: 20, maxLength: 500 }),
    brandMandatories: fc.array(fc.string({ minLength: 5, maxLength: 100 }), {
      maxLength: 5,
    }),
    targetAudience: fc.string({ minLength: 10, maxLength: 200 }),
  });

export const conceptGenerator = (): fc.Arbitrary<Concept> =>
  fc.record({
    id: fc.uuid(),
    title: fc.string({ minLength: 5, maxLength: 100 }),
    description: fc.string({ minLength: 20, maxLength: 500 }),
    keyMessage: fc.string({ minLength: 10, maxLength: 200 }),
    visualStyle: fc.string({ minLength: 10, maxLength: 100 }),
    generatedAt: fc.date(),
    version: fc.integer({ min: 1, max: 10 }),
  });

export const sceneGenerator = (): fc.Arbitrary<Scene> =>
  fc.record({
    sceneNumber: fc.integer({ min: 1, max: 20 }),
    duration: fc.integer({ min: 1, max: 30 }),
    description: fc.string({ minLength: 20, maxLength: 300 }),
  });

export const screenplayGenerator = (): fc.Arbitrary<Screenplay> =>
  fc.record({
    id: fc.uuid(),
    variant: fc.string({ minLength: 5, maxLength: 50 }),
    scenes: fc.array(sceneGenerator(), { minLength: 3, maxLength: 10 }),
    totalDuration: fc.integer({ min: 15, max: 120 }),
    scores: fc.record({
      clarity: fc.float({ min: 0, max: 10 }),
      feasibility: fc.float({ min: 0, max: 10 }),
      costRisk: fc.float({ min: 0, max: 10 }),
    }),
    generatedAt: fc.date(),
  });

export const storyboardSceneGenerator = (): fc.Arbitrary<StoryboardScene> =>
  fc.record({
    sceneNumber: fc.integer({ min: 1, max: 20 }),
    imageUrl: fc.oneof(fc.webUrl(), fc.constant(null)),
    description: fc.string({ minLength: 20, maxLength: 300 }),
    cameraAngle: fc.constantFrom(
      'Wide Shot',
      'Medium Shot',
      'Close-up',
      'Over-the-shoulder',
      'POV'
    ),
    cameraMovement: fc.option(fc.constantFrom(
      'Static',
      'Pan',
      'Tilt',
      'Zoom',
      'Dolly',
      'Tracking'
    )),
    onScreenText: fc.option(fc.string({ maxLength: 100 })),
    audioNotes: fc.option(fc.string({ minLength: 10, maxLength: 200 })),
    dialogue: fc.option(fc.string({ minLength: 10, maxLength: 200 })),
    notes: fc.option(fc.string({ minLength: 10, maxLength: 200 })),
    duration: fc.integer({ min: 1, max: 30 }),
  });

export const storyboardGenerator = (): fc.Arbitrary<Storyboard> =>
  fc.record({
    id: fc.uuid(),
    scenes: fc.array(storyboardSceneGenerator(), {
      minLength: 3,
      maxLength: 10,
    }),
    styleSettings: fc.option(fc.record({
      styleLock: fc.boolean(),
      characterLock: fc.boolean(),
    })),
    generatedAt: fc.date(),
    version: fc.option(fc.integer({ min: 1, max: 10 })),
  });

export const warningGenerator = (): fc.Arbitrary<Warning> =>
  fc.record({
    severity: fc.constantFrom('low', 'medium', 'high', 'critical'),
    category: fc.constantFrom('legal', 'brand', 'location', 'budget', 'risk'),
    message: fc.string({ minLength: 10, maxLength: 200 }),
    affectedItems: fc.array(fc.string({ minLength: 3, maxLength: 50 }), {
      maxLength: 5,
    }),
  });

export const assumptionGenerator = (): fc.Arbitrary<Assumption> =>
  fc.record({
    id: fc.uuid(),
    category: fc.string({ minLength: 3, maxLength: 50 }),
    original: fc.string({ minLength: 10, maxLength: 200 }),
    override: fc.option(fc.string({ minLength: 10, maxLength: 200 })),
    editedBy: fc.option(fc.string({ minLength: 3, maxLength: 50 })),
    editedAt: fc.option(fc.date()),
  });

export const changelogEntryGenerator = (): fc.Arbitrary<ChangelogEntry> =>
  fc.record({
    timestamp: fc.date(),
    documentType: documentTypeGenerator(),
    changes: fc.array(fc.string({ minLength: 10, maxLength: 200 }), {
      minLength: 1,
      maxLength: 10,
    }),
    triggeredBy: fc.constantFrom<'regeneration' | 'user_edit'>(
      'regeneration',
      'user_edit'
    ),
  });

export const productionDocumentGenerator =
  (): fc.Arbitrary<ProductionDocument> =>
    fc.record({
      type: documentTypeGenerator(),
      status: documentStatusGenerator(),
      content: fc.anything(),
      warnings: fc.array(warningGenerator(), { maxLength: 5 }),
      lastUpdated: fc.date(),
    });

export const productionPackGenerator = (): fc.Arbitrary<ProductionPack> =>
  fc.record({
    id: fc.uuid(),
    generatedAt: fc.date(),
    budget: fc.option(fc.record({
      total_min: fc.float({ min: 1000, max: 100000 }),
      total_max: fc.float({ min: 1000, max: 100000 }),
      line_items: fc.array(fc.record({
        category: fc.string({ minLength: 3, maxLength: 50 }),
        item: fc.string({ minLength: 3, maxLength: 100 }),
        quantity: fc.integer({ min: 1, max: 100 }),
        unit_cost: fc.float({ min: 10, max: 10000 }),
        total_cost: fc.float({ min: 10, max: 100000 }),
      }), { maxLength: 10 }),
    })),
    schedule: fc.option(fc.record({
      total_shoot_days: fc.integer({ min: 1, max: 30 }),
      days: fc.array(fc.record({
        day: fc.integer({ min: 1, max: 30 }),
        location: fc.string({ minLength: 3, maxLength: 100 }),
        scenes: fc.array(fc.integer({ min: 1, max: 20 }), { maxLength: 10 }),
      }), { maxLength: 30 }),
    })),
    crew: fc.option(fc.array(fc.record({
      role: fc.string({ minLength: 3, maxLength: 50 }),
      responsibilities: fc.string({ minLength: 10, maxLength: 200 }),
    }), { maxLength: 20 })),
    locations: fc.option(fc.array(fc.record({
      name: fc.string({ minLength: 3, maxLength: 100 }),
      type: fc.constantFrom('INT', 'EXT'),
      requirements: fc.string({ minLength: 10, maxLength: 200 }),
    }), { maxLength: 10 })),
    equipment: fc.option(fc.array(fc.record({
      item: fc.string({ minLength: 3, maxLength: 100 }),
      quantity: fc.integer({ min: 1, max: 100 }),
    }), { maxLength: 20 })),
    legal: fc.option(fc.array(fc.anything(), { maxLength: 5 })),
  });

export const projectGenerator = (): fc.Arbitrary<Project> =>
  fc.record({
    id: fc.uuid(),
    name: fc.string({ minLength: 5, maxLength: 100 }),
    client: fc.string({ minLength: 3, maxLength: 100 }),
    status: projectStatusGenerator(),
    createdAt: fc.date(),
    updatedAt: fc.date(),
    currentStep: workflowStepGenerator(),
    brief: fc.option(briefGenerator()),
    concept: fc.option(conceptGenerator()),
    screenplays: fc.option(fc.array(screenplayGenerator(), { maxLength: 2 })),
    selectedScreenplay: fc.option(fc.uuid()),
    storyboard: fc.option(storyboardGenerator()),
    productionPack: fc.option(productionPackGenerator()),
    tags: fc.array(fc.string({ minLength: 2, maxLength: 20 }), {
      maxLength: 5,
    }),
    budgetBand: budgetBandGenerator(),
  });
