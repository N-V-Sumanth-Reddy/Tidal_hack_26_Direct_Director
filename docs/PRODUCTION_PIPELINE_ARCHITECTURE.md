# Production Pipeline Architecture

## Overview

The production pipeline generates comprehensive production planning data from a storyboard. It uses **TAMUS LLM** (not Tavily search) to analyze the storyboard and generate realistic production planning artifacts.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (UI)                             │
│  - User submits brief                                        │
│  - Generates concept, screenplays, storyboard               │
│  - Clicks "Generate Production Pack"                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (FastAPI)                               │
│  POST /api/projects/{id}/generate/production                │
│  - Creates background job                                    │
│  - Calls production pipeline nodes                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         PRODUCTION PIPELINE (ad_production_pipeline.py)      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Scene Breakdown Node                             │  │
│  │     - Analyzes storyboard                            │  │
│  │     - Creates structured scene plan                  │  │
│  │     - Defines shots for each scene                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  2. Parallel Planning Nodes (run simultaneously)     │  │
│  │                                                       │  │
│  │  ┌─────────────────────┐  ┌────────────────────────┐│  │
│  │  │ Location Planning   │  │ Budget Estimation      ││  │
│  │  │ - Location reqs     │  │ - Line items           ││  │
│  │  │ - Permits needed    │  │ - Min/max ranges       ││  │
│  │  └─────────────────────┘  └────────────────────────┘│  │
│  │                                                       │  │
│  │  ┌─────────────────────┐  ┌────────────────────────┐│  │
│  │  │ Schedule Planning   │  │ Crew & Gear            ││  │
│  │  │ - Shoot days        │  │ - Crew roles           ││  │
│  │  │ - Scene grouping    │  │ - Equipment list       ││  │
│  │  └─────────────────────┘  └────────────────────────┘│  │
│  │                                                       │  │
│  │  ┌─────────────────────┐  ┌────────────────────────┐│  │
│  │  │ Legal Clearances    │  │ Risk Register          ││  │
│  │  │ - Talent releases   │  │ - Safety risks         ││  │
│  │  │ - Location permits  │  │ - Mitigation plans     ││  │
│  │  └─────────────────────┘  └────────────────────────┘│  │
│  └──────────────────────────────────────────────────────┘  │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  3. Format & Return Production Pack                  │  │
│  │     - Combines all node outputs                      │  │
│  │     - Returns structured JSON                        │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   TAMUS LLM API                              │
│  - Receives prompts from each node                           │
│  - Generates JSON responses (may include markdown)           │
│  - Returns production planning data                          │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Input (from Storyboard):
```json
{
  "scenes": [
    {
      "sceneNumber": 1,
      "duration": 5,
      "description": "Opening shot of product in nature",
      "dialogue": "Voiceover: 'Innovation meets sustainability'",
      "cameraAngle": "Wide establishing shot"
    },
    // ... more scenes
  ]
}
```

### Processing (Each Node):

#### 1. Scene Breakdown Node
**Input**: Storyboard text
**LLM Prompt**: "Convert storyboard into structured scene plan with shots..."
**Output**:
```json
{
  "scenes": [
    {
      "scene_id": "S1",
      "duration_sec": 5,
      "location_type": "EXT",
      "time_of_day": "DAY",
      "location_description": "Forest clearing",
      "cast_count": 1,
      "props": ["smartphone", "natural elements"],
      "wardrobe": ["casual outdoor wear"]
    }
  ],
  "shots": [
    {
      "shot_id": "S1-001",
      "scene_id": "S1",
      "shot_type": "WIDE",
      "camera_movement": "DOLLY",
      "duration_sec": 5,
      "description": "Sweeping dolly shot through forest"
    }
  ]
}
```

#### 2. Location Planning Node
**Input**: Scene plan (locations from scenes)
**LLM Prompt**: "Generate location requirements for these scenes..."
**Output**:
```json
{
  "locations": [
    {
      "name": "Forest Clearing",
      "type": "EXT",
      "requirements": "Natural lighting, accessible by vehicle",
      "alternates": ["City park", "Botanical garden"],
      "permits_required": ["Park filming permit", "Insurance certificate"]
    }
  ]
}
```

#### 3. Budget Estimation Node
**Input**: Scene plan (complexity, cast count, etc.)
**LLM Prompt**: "Generate detailed budget for this production..."
**Output**:
```json
{
  "total_min": 45000,
  "total_max": 75000,
  "line_items": [
    {
      "category": "Crew",
      "item": "Director",
      "quantity": 1,
      "unit_cost": 2500,
      "total_cost": 2500
    },
    {
      "category": "Equipment",
      "item": "Camera package",
      "quantity": 1,
      "unit_cost": 1200,
      "total_cost": 1200
    }
  ],
  "assumptions": ["10-hour shoot days", "Local crew rates"],
  "cost_drivers": ["Location fees", "Equipment rental"]
}
```

#### 4. Schedule Planning Node
**Input**: Scene plan (scenes grouped by location)
**LLM Prompt**: "Generate shoot schedule grouping scenes by location..."
**Output**:
```json
{
  "total_shoot_days": 3,
  "days": [
    {
      "day": 1,
      "location": "Forest Clearing",
      "scenes": ["S1", "S2", "S3"],
      "setup_time_hours": 2,
      "shoot_time_hours": 6
    }
  ],
  "company_moves": [
    {
      "from": "Forest Clearing",
      "to": "Urban Street",
      "estimated_time_hours": 1.5
    }
  ]
}
```

#### 5. Crew & Gear Node
**Input**: Scene plan (complexity, technical requirements)
**LLM Prompt**: "Generate crew and equipment recommendations..."
**Output**:
```json
{
  "crew": [
    {
      "role": "Director",
      "responsibilities": "Creative direction, shot composition",
      "required": true
    },
    {
      "role": "Director of Photography",
      "responsibilities": "Camera operation, lighting design",
      "required": true
    }
  ],
  "equipment": [
    {
      "item": "Cinema camera (RED/ARRI)",
      "quantity": 1,
      "required": true
    },
    {
      "item": "Lighting kit",
      "quantity": 1,
      "required": true
    }
  ]
}
```

#### 6. Legal Clearances Node
**Input**: Scene plan (cast count, locations, props)
**LLM Prompt**: "Generate legal clearances checklist..."
**Output**:
```json
{
  "items": [
    {
      "item": "Talent releases",
      "description": "Required for all on-camera talent",
      "quantity": 5,
      "high_risk": false
    },
    {
      "item": "Location permits",
      "description": "Filming permits for public spaces",
      "quantity": 2,
      "high_risk": true
    }
  ]
}
```

#### 7. Risk Register Node
**Input**: Scene plan (exterior scenes, night scenes, stunts)
**LLM Prompt**: "Generate risk and safety register..."
**Output**:
```json
{
  "risks": [
    {
      "risk": "Weather delays",
      "likelihood": "MEDIUM",
      "impact": "HIGH",
      "mitigation": "Have backup indoor location, monitor forecast"
    },
    {
      "risk": "Equipment failure",
      "likelihood": "LOW",
      "impact": "HIGH",
      "mitigation": "Backup camera body, test all equipment day before"
    }
  ]
}
```

### Final Output (to Frontend):
```json
{
  "productionPack": {
    "id": "uuid",
    "generatedAt": "2026-02-08T10:30:00Z",
    "scenePlan": { /* scene breakdown */ },
    "budget": { /* budget estimate */ },
    "schedule": { /* schedule plan */ },
    "locations": [ /* locations */ ],
    "crew": [ /* crew list */ ],
    "equipment": [ /* equipment list */ ],
    "legal": [ /* legal clearances */ ],
    "risks": [ /* risk register */ ]
  }
}
```

## Key Technologies

### TAMUS LLM (GPT-5.2)
- **Purpose**: Generate all production planning data
- **Model**: `protected.gpt-5.2`
- **Max Tokens**: 2000 per request
- **Response Format**: Text (may include JSON in markdown)

### NO Tavily Search
- Production planning doesn't need web search
- All data is generated from the storyboard analysis
- LLM has sufficient knowledge of production planning

### JSON Extraction
- **Challenge**: LLM returns JSON wrapped in markdown
- **Solution**: `extract_json_from_llm_response()` function
- **Handles**: Code blocks, explanatory text, various formats

## Error Handling

### Graceful Degradation
Each node can fail independently without breaking the entire pipeline:

```python
try:
    clean_json = extract_json_from_llm_response(llm_response)
    data = json.loads(clean_json)
    return {"node_data": data}
except json.JSONDecodeError:
    # Return empty structure, allow pipeline to continue
    return {"node_data": {}}
```

### Partial Results
If some nodes fail, the backend uses whatever data was successfully generated:

```python
except Exception as error:
    # Use partial results instead of dummy data
    project["productionPack"] = {
        "scenePlan": state.get("scene_plan", {}),  # May be empty
        "budget": state.get("budget_estimate", {}),  # May be empty
        # ... other nodes
        "error": str(error)  # For debugging
    }
```

## Performance

### Parallel Execution
Nodes 2-7 run in parallel using `asyncio.to_thread()`:
- **Sequential**: ~60 seconds (7 nodes × ~8-10 seconds each)
- **Parallel**: ~15-20 seconds (longest node + overhead)

### Progress Updates
```python
job["progress"] = 10   # Starting
job["progress"] = 20   # Scene breakdown
job["progress"] = 40   # Parallel nodes started
job["progress"] = 90   # Formatting
job["progress"] = 100  # Complete
```

## Debugging

### Enable Verbose Logging
```bash
# In backend logs, look for:
✓ Generated scene plan with 6 scenes
✓ Generated budget estimate: $45,000 - $75,000
⚠ Error parsing schedule: Expecting value...
  Response preview: Here's the schedule...
```

### Check Response Previews
When JSON parsing fails, the first 200 characters of the LLM response are logged to help identify the issue.

### Verify TAMUS API
```bash
# Check if TAMUS_API_KEY is set
echo $TAMUS_API_KEY

# Check if TAMUS_MODEL is correct
echo $TAMUS_MODEL  # Should be "protected.gpt-5.2"
```

## Summary

The production pipeline:
- ✅ Uses **TAMUS LLM only** (no Tavily search)
- ✅ Generates **7 types of production planning data**
- ✅ Runs **6 nodes in parallel** for speed
- ✅ Handles **JSON parsing robustly**
- ✅ Provides **graceful degradation** on errors
- ✅ Returns **real data** instead of dummy data

All production planning is AI-generated based on analyzing the storyboard with TAMUS GPT-5.2.
