# LangGraph Integration Summary

## Current Status

✅ **LangGraph workflow created** (`backend/ad_workflow.py`)
✅ **Dependencies installed** (langgraph, langchain, langchain-core)
❌ **Not yet integrated with FastAPI backend**

## Integration Options

### Option 1: Replace Existing Flow (Recommended)

Replace the current concept + screenplay generation with the LangGraph workflow.

**Pros**:
- Uses exact notebook architecture
- Agent-based approach for better quality
- Parallel screenplay generation
- Cleaner code

**Cons**:
- Requires testing to ensure compatibility
- Need to update frontend if data structure changes

### Option 2: Add New Endpoint (Safer)

Add a new endpoint `/api/projects/{project_id}/generate/langgraph` that uses the workflow.

**Pros**:
- Keeps existing functionality as fallback
- Can test without breaking current flow
- Easy to compare results

**Cons**:
- Duplicate code
- Need to maintain two approaches

### Option 3: Feature Flag (Best of Both)

Add a feature flag to switch between old and new approach.

**Pros**:
- Can toggle between approaches
- Easy rollback if issues
- Gradual migration

**Cons**:
- More complex code
- Need to maintain both temporarily

## Recommended Approach

**Use Option 3 (Feature Flag)** with these steps:

1. Add environment variable `USE_LANGGRAPH=true/false`
2. Update `run_generation()` to check the flag
3. If true, use LangGraph workflow
4. If false, use existing approach
5. Test thoroughly with frontend
6. Once stable, remove old code

## Implementation Steps

### Step 1: Add Feature Flag

```python
# In backend/main.py
USE_LANGGRAPH = os.getenv("USE_LANGGRAPH", "false").lower() == "true"
```

### Step 2: Update run_generation()

```python
if step == "concept" or step == "screenplays":
    if USE_LANGGRAPH:
        # Use LangGraph workflow
        await run_langgraph_workflow(job, project, params)
    else:
        # Use existing approach
        # ... existing code ...
```

### Step 3: Create Integration Function

```python
async def run_langgraph_workflow(job, project, params):
    """Run LangGraph workflow for concept + screenplays"""
    from ad_workflow import run_ad_workflow
    
    # Build theme from brief
    brief = params.get("brief", project.get("brief", {}))
    theme = f"""
    Platform: {brief.get('platform', 'YouTube')}
    Duration: {brief.get('duration', 30)} seconds
    Budget: ${brief.get('budget', 50000):,}
    Creative Direction: {brief.get('creativeDirection', '')}
    Brand: {', '.join(brief.get('brandMandatories', []))}
    Target Audience: {brief.get('targetAudience', '')}
    """
    
    # Run workflow
    result = await run_ad_workflow(theme)
    
    # Store results in project
    project["concept"] = {
        "id": str(uuid.uuid4()),
        "title": result["concept"][:100],
        "description": result["concept"],
        "generatedAt": datetime.now().isoformat()
    }
    
    # Parse and store screenplays
    # ... parse result["screenplay_1"] and result["screenplay_2"] ...
```

### Step 4: Test

1. Set `USE_LANGGRAPH=true` in `.env`
2. Restart backend
3. Test with frontend
4. Compare results with old approach

### Step 5: Deploy

Once stable:
1. Remove old code
2. Remove feature flag
3. Update documentation

## Current Blocker

The LangGraph workflow is ready but needs:

1. **Integration function** to connect workflow output to FastAPI data structures
2. **Scene parsing** from screenplay text to structured scenes
3. **Testing** to ensure frontend compatibility

## Next Steps

Would you like me to:

1. ✅ **Implement Option 3 (Feature Flag)** - Add the integration with a toggle
2. ⏸️ **Implement Option 2 (New Endpoint)** - Add separate endpoint for testing
3. ⏸️ **Implement Option 1 (Replace)** - Directly replace existing code

**Recommendation**: Start with Option 3 (Feature Flag) for safe, gradual migration.
