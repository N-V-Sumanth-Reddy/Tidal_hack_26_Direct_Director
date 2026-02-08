import type {
  Project,
  Brief,
  Concept,
  Screenplay,
  Storyboard,
  ProductionPack,
} from '@/lib/types';

// ============================================================================
// Test Fixtures
// ============================================================================

export const mockBrief: Brief = {
  platform: 'YouTube',
  duration: 30,
  budget: 50000,
  location: 'Urban cityscape',
  constraints: ['No animals', 'Daytime shooting only'],
  creativeDirection:
    'Modern, energetic ad showcasing product features with dynamic visuals',
  brandMandatories: ['Logo visible for 3 seconds', 'Use brand colors'],
  targetAudience: 'Tech-savvy millennials aged 25-35',
};

export const mockConcept: Concept = {
  id: 'concept-1',
  title: 'Urban Energy',
  description:
    'A fast-paced journey through city life showing how our product fits seamlessly into modern lifestyles',
  keyMessage: 'Empowering your everyday',
  visualStyle: 'Cinematic with vibrant colors and dynamic camera movements',
  generatedAt: new Date('2024-01-15'),
  version: 1,
};

export const mockScreenplayA: Screenplay = {
  id: 'screenplay-a',
  variant: 'A (Rajamouli Style)',
  scenes: [
    {
      sceneNumber: 1,
      duration: 5,
      description: 'Busy morning commute with people rushing through city street',
    },
    {
      sceneNumber: 2,
      duration: 10,
      description: 'Protagonist uses product while waiting for coffee in coffee shop',
    },
  ],
  totalDuration: 30,
  scores: {
    clarity: 8.5,
    feasibility: 7.0,
    costRisk: 6.5,
  },
  generatedAt: new Date('2024-01-16'),
};

export const mockScreenplayB: Screenplay = {
  id: 'screenplay-b',
  variant: 'B (Shankar Style)',
  scenes: [
    {
      sceneNumber: 1,
      duration: 8,
      description: 'Golden hour shot of city skyline from rooftop',
    },
    {
      sceneNumber: 2,
      duration: 12,
      description: 'Protagonist demonstrates product features on rooftop with city backdrop',
    },
  ],
  totalDuration: 30,
  scores: {
    clarity: 7.5,
    feasibility: 8.5,
    costRisk: 7.0,
  },
  generatedAt: new Date('2024-01-16'),
};

export const mockStoryboard: Storyboard = {
  id: 'storyboard-1',
  scenes: [
    {
      sceneNumber: 1,
      imageUrl: 'https://example.com/scene1.jpg',
      description: 'Wide shot of busy city street at morning rush hour',
      cameraAngle: 'Wide Shot',
      cameraMovement: 'Tracking',
      onScreenText: '',
      audioNotes: 'Upbeat music, city ambience',
      duration: 5,
    },
    {
      sceneNumber: 2,
      imageUrl: 'https://example.com/scene2.jpg',
      description: 'Close-up of hands using product',
      cameraAngle: 'Close-up',
      cameraMovement: 'Static',
      onScreenText: 'Start your day right',
      audioNotes: 'Voiceover, soft background music',
      duration: 10,
    },
  ],
  styleSettings: {
    styleLock: true,
    characterLock: false,
  },
  generatedAt: new Date('2024-01-17'),
  version: 1,
};

export const mockProductionPack: ProductionPack = {
  id: 'production-pack-1',
  generatedAt: new Date('2024-01-18'),
  budget: {
    total_min: 15000,
    total_max: 25000,
    line_items: [
      {
        category: 'Crew',
        item: 'Director',
        quantity: 1,
        unit_cost: 1500,
        total_cost: 1500,
      },
      {
        category: 'Equipment',
        item: 'Camera package',
        quantity: 1,
        unit_cost: 800,
        total_cost: 800,
      },
    ],
  },
  schedule: {
    total_shoot_days: 2,
    days: [
      {
        day: 1,
        location: 'Studio',
        scenes: [1, 2, 3],
      },
      {
        day: 2,
        location: 'Urban setting',
        scenes: [4, 5],
      },
    ],
  },
  crew: [
    {
      role: 'Director',
      responsibilities: 'Overall creative direction',
    },
    {
      role: 'DP',
      responsibilities: 'Camera and lighting',
    },
  ],
  locations: [
    {
      name: 'Studio',
      type: 'INT',
      requirements: 'Green screen, lighting grid',
    },
    {
      name: 'Urban setting',
      type: 'EXT',
      requirements: 'Permits, parking',
    },
  ],
  equipment: [
    {
      item: 'Camera package',
      quantity: 1,
    },
    {
      item: 'Lighting kit',
      quantity: 1,
    },
  ],
  legal: [],
};

export const mockProject: Project = {
  id: 'project-1',
  name: 'Urban Energy Campaign',
  client: 'TechCorp',
  status: 'in_progress',
  createdAt: new Date('2024-01-15'),
  updatedAt: new Date('2024-01-18'),
  currentStep: 'storyboard',
  brief: mockBrief,
  concept: mockConcept,
  screenplays: [mockScreenplayA, mockScreenplayB],
  selectedScreenplay: 'screenplay-a',
  storyboard: mockStoryboard,
  productionPack: mockProductionPack,
  tags: ['tech', 'urban', 'lifestyle'],
  budgetBand: 'medium',
};

export const mockProjects: Project[] = [
  mockProject,
  {
    ...mockProject,
    id: 'project-2',
    name: 'Summer Collection Launch',
    client: 'FashionBrand',
    status: 'draft',
    currentStep: 'brief',
    tags: ['fashion', 'summer'],
    budgetBand: 'high',
  },
  {
    ...mockProject,
    id: 'project-3',
    name: 'Product Demo Video',
    client: 'StartupXYZ',
    status: 'approved',
    currentStep: 'export',
    tags: ['product', 'demo'],
    budgetBand: 'low',
  },
];
