# Backend-Frontend Type Mapping

This document maps the exact data structures returned by the backend API to the TypeScript types used in the frontend.

## Backend Data Structures (Python/FastAPI)

### 1. Project
```python
{
    "id": str,
    "name": str,
    "client": str,
    "status": "draft" | "in_progress" | "needs_review" | "approved" | "archived",
    "createdAt": str (ISO datetime),
    "updatedAt": str (ISO datetime),
    "currentStep": "brief" | "concept" | "screenplays" | "select" | "storyboard" | "production" | "export",
    "tags": List[str],
    "budgetBand": "low" | "medium" | "high" | "premium",
    "brief": Brief (optional),
    "concept": Concept (optional),
    "screenplays": List[Screenplay] (optional),
    "selectedScreenplay": str (optional - screenplay ID),
    "storyboard": Storyboard (optional),
    "productionPack": ProductionPack (optional)
}
```

### 2. Brief
```python
{
    "platform": str,
    "duration": int,  # seconds
    "budget": float,
    "location": str,
    "constraints": List[str],
    "creativeDirection": str,
    "brandMandatories": List[str],
    "targetAudience": str
}
```

### 3. Concept
```python
{
    "id": str,
    "title": str,
    "description": str,
    "keyMessage": str,
    "visualStyle": str,
    "generatedAt": str (ISO datetime),
    "version": int
}
```

### 4. Screenplay
```python
{
    "id": str,
    "variant": str,  # "A (Rajamouli Style)" or "B (Shankar Style)"
    "scenes": List[Scene],
    "totalDuration": int,
    "scores": {
        "clarity": float,
        "feasibility": float,
        "costRisk": float
    },
    "generatedAt": str (ISO datetime)
}
```

### 5. Scene (in Screenplay)
```python
{
    "sceneNumber": int,
    "duration": int,
    "description": str
}
```

### 6. Storyboard
```python
{
    "id": str,
    "generatedAt": str (ISO datetime),
    "scenes": List[StoryboardScene]
}
```

### 7. StoryboardScene
```python
{
    "id": str,
    "sceneNumber": int,
    "duration": int,
    "description": str,
    "dialogue": str | None,
    "cameraAngle": str,
    "notes": str,
    "imageUrl": str | None
}
```

### 8. ProductionPack
```python
{
    "id": str,
    "generatedAt": str (ISO datetime),
    "budget": {
        "total_min": float,
        "total_max": float,
        "line_items": List[{
            "category": str,
            "item": str,
            "quantity": int,
            "unit_cost": float,
            "total_cost": float
        }]
    },
    "schedule": {
        "total_shoot_days": int,
        "days": List[{
            "day": int,
            "location": str,
            "scenes": List[int]
        }]
    },
    "crew": List[{
        "role": str,
        "responsibilities": str
    }],
    "locations": List[{
        "name": str,
        "type": str,  # "INT" or "EXT"
        "requirements": str
    }],
    "equipment": List[{
        "item": str,
        "quantity": int
    }],
    "legal": List[Any]  # Empty for now
}
```

## Frontend TypeScript Types (Required Updates)

### Issues Found:
1. ✅ **StoryboardScene** - Fixed: Changed `visualDescription` to `description`, added `dialogue`, `notes`, made `imageUrl` nullable
2. ✅ **ProductionPack** - Fixed: Changed from nested `documents` structure to flat structure matching backend
3. ⚠️ **ProductionPack.budget** - Needs update: Backend uses `total_min`, `total_max`, `line_items` but frontend expects `total`, `preProduction`, `production`, `breakdown`
4. ⚠️ **ProductionPack.schedule** - Needs update: Backend uses `total_shoot_days`, `days[].day` but frontend expects `days[].dayNumber`, `days[].date`, `days[].description`, `days[].duration`
5. ⚠️ **ProductionPack.crew** - Needs update: Backend only has `role`, `responsibilities` but frontend expects `count` too
6. ⚠️ **ProductionPack.locations** - Needs update: Backend has `type`, `requirements` but frontend expects `address`, `scenes`, `permitRequired`, `notes`
7. ⚠️ **Scene** (in Screenplay) - Missing fields: Frontend expects `location`, `timeOfDay`, `dialogue`, `action` but backend only provides `sceneNumber`, `duration`, `description`

## Recommended Fix Strategy

**Option 1: Update Backend to Match Frontend (More Work)**
- Modify backend to return richer data structures
- Better long-term solution

**Option 2: Update Frontend to Match Backend (Faster)**
- Update TypeScript types to match what backend actually returns
- Update UI components to work with simpler data
- Faster to implement

**Option 3: Hybrid Approach (Recommended)**
- Keep backend simple for MVP
- Update frontend types to match backend
- Add data transformation layer in frontend if needed
- Plan backend enhancements for v2
