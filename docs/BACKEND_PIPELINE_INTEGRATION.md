# Backend Pipeline Integration Guide

## Overview

The backend now uses the **production pipeline** (`ad_production_pipeline_web.py`) instead of direct TAMUS API calls. This provides:

✅ **Better quality output** - Uses the full LangGraph pipeline
✅ **Gemini 2.5 Flash images** - Storyboard frames with actual images
✅ **Comprehensive production planning** - Scene breakdown, budget, schedule, etc.
✅ **No HITL gates** - Auto-approves for web UI (no command-line prompts)

## Architecture

```
Frontend (Next.js)
    ↓
Backend (FastAPI) - backend/main.py
    ↓
Pipeline Integration - backend/pipeline_integration.py
    ↓
Production Pipeline - ad_production_pipeline_web.py
    ↓
TAMUS API + Gemini API
```

## Files Created

### 1. `ad_production_pipeline_web.py`
- Web-compatible version of the production pipeline
- **No HITL gates** (auto-approves everything)
- Uses Gemini 2.5 Flash for storyboard images
- Returns structured data for API responses

### 2. `backend/pipeline_integration.py`
- Integrates pipeline with FastAPI backend
- **Step-by-step execution** with state caching
- Async wrappers for each generation step
- Manages pipeline state across requests

## How It Works

### State Caching

The pipeline runner caches state for each project:

```python
{
    "project_123": {
        "theme": "Sustainable technology",
        "concept": "Generated concept...",
        "screenplay_1": "Rajamouli screenplay...",
        "screenplay_2": "Shankar screenplay...",
        "screenplay_winner": "Selected screenplay...",
        "story_board": "Storyboard text...",
        "storyboard_frames": [...]  # With Gemini images!
    }
}
```

### Step-by-Step Execution

1. **Generate Concept**
   ```python
   runner = get_pipeline_runner()
   result = await runner.generate_concept(project_id, brief)
   # Returns: {"concept": "...", "status": "completed"}
   ```

2. **Generate Screenplays**
   ```python
   result = await runner.generate_screenplays(project_id, brief)
   # Returns: {"screenplay_1": "...", "screenplay_2": "...", "status": "completed"}
   ```

3. **Select Screenplay**
   ```python
   await runner.select_screenplay(project_id, screenplay_id)
   # Sets screenplay_winner in cached state
   ```

4. **Generate Storyboard** (with Gemini images!)
   ```python
   result = await runner.generate_storyboard(project_id, brief)
   # Returns: {"storyboard": "...", "storyboard_frames": [...], "status": "completed"}
   ```

5. **Generate Production Pack**
   ```python
   result = await runner.generate_production_pack(project_id, brief)
   # Returns: {"budget": {...}, "schedule": {...}, ...}
   ```

## Integration Steps

### Option 1: Quick Test (Recommended First)

Test the pipeline integration without modifying the backend:

```bash
# Test the web pipeline directly
python -c "
import asyncio
from backend.pipeline_integration import get_pipeline_runner

async def test():
    runner = get_pipeline_runner()
    brief = {
        'brand_name': 'EcoPhone',
        'theme': 'Sustainable technology',
        'target_duration_sec': 30,
        'aspect_ratio': '16:9'
    }
    
    # Test concept generation
    result = await runner.generate_concept('test-123', brief)
    print('Concept:', result['concept'][:100])
    
    # Test screenplay generation
    result = await runner.generate_screenplays('test-123', brief)
    print('Screenplays generated')
    
    # Test storyboard with Gemini images
    result = await runner.generate_storyboard('test-123', brief)
    print('Storyboard frames:', len(result['storyboard_frames']))
    for frame in result['storyboard_frames']:
        print(f\"  Frame {frame['frame_number']}: {frame['image_url'] or 'No image'}\")

asyncio.run(test())
"
```

### Option 2: Full Backend Integration

Modify `backend/main.py` to use the pipeline:

```python
# At the top of backend/main.py, add:
from pipeline_integration import get_pipeline_runner

# In run_generation function, replace TAMUS calls with:
runner = get_pipeline_runner()

if step == "concept":
    result = await runner.generate_concept(project_id, params["brief"])
    project["concept"] = {
        "id": str(uuid.uuid4()),
        "description": result["concept"],
        ...
    }

elif step == "screenplays":
    result = await runner.generate_screenplays(project_id, project["brief"])
    # Parse and store screenplays...

elif step == "storyboard":
    result = await runner.generate_storyboard(project_id, project["brief"])
    project["storyboard"] = {
        "scenes": result["storyboard_frames"]  # Now with Gemini images!
    }

elif step == "production":
    result = await runner.generate_production_pack(project_id, project["brief"])
    project["productionPack"] = result
```

## Benefits

### Before (Direct TAMUS Calls)
- ❌ No Gemini images
- ❌ Simple text generation
- ❌ No structured scene breakdown
- ❌ Basic production pack

### After (Production Pipeline)
- ✅ **Gemini 2.5 Flash images** for storyboard
- ✅ **Structured scene breakdown** with shots
- ✅ **Comprehensive production planning**
- ✅ **Better quality output** from full pipeline

## Testing

### 1. Test Pipeline Integration

```bash
cd backend
python -c "from pipeline_integration import get_pipeline_runner; print('✓ Import successful')"
```

### 2. Test Gemini Integration

```bash
# Ensure GEMINI_API_KEY is set
echo $GEMINI_API_KEY

# Test storyboard generation
python test_gemini_storyboard.py
```

### 3. Test Full Backend

```bash
# Start backend
cd backend
uvicorn main:app --reload --port 8000

# In another terminal, test API
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "client": "Test Client", "tags": [], "budgetBand": "medium"}'
```

## Troubleshooting

### Issue: "Pipeline not initialized"
**Solution**: Check that `ad_production_pipeline_web.py` is in the parent directory

### Issue: "No Gemini images generated"
**Solution**: Verify `GEMINI_API_KEY` is set in `.env` file

### Issue: "Import error: google.genai"
**Solution**: Install package: `pip install google-genai>=0.8.0`

### Issue: "State not found"
**Solution**: The pipeline caches state per project. Ensure you're using the same `project_id` across requests.

## Performance Considerations

- **State Caching**: Pipeline state is cached in memory (not persistent)
- **Async Execution**: All pipeline nodes run in thread pool executor
- **Gemini Rate Limits**: Image generation is sequential to avoid rate limits
- **Memory Usage**: Each project's state is cached until cleared

## Next Steps

1. ✅ Test pipeline integration (Option 1)
2. ⏳ Integrate with backend (Option 2)
3. ⏳ Test end-to-end with frontend
4. ⏳ Add error handling and retry logic
5. ⏳ Implement state persistence (database)

## Summary

The backend can now use the production pipeline for **better quality output** with **Gemini images**. The integration is designed to be:

- **Non-breaking**: Can be tested without modifying existing backend
- **Step-by-step**: Executes pipeline nodes individually
- **Cached**: Maintains state across requests
- **Async**: Doesn't block the event loop

Ready to integrate! 🚀
