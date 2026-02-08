# Production Pipeline Analysis - Why Dummy Data is Showing

## Problem Summary

The production pack in the UI is showing dummy/empty data:
- Budget: $0 - $0
- Shoot Days: 0
- Locations: 0
- All sections showing "No data available"

## Root Cause Analysis

### 1. **JSON Parsing Failures**

The production pipeline nodes in `ad_production_pipeline.py` are calling TAMUS LLM and expecting **strict JSON responses**:

```python
def scene_breakdown_node(state: State) -> Dict:
    prompt = f"""...Generate a scene plan in strict JSON format...
    Return ONLY valid JSON, no additional text."""
    
    scene_plan_json = call_tamus_api(prompt)
    
    try:
        scene_plan = json.loads(scene_plan_json)  # ❌ FAILS HERE
        return {"scene_plan": scene_plan}
    except json.JSONDecodeError as e:
        print(f"Error parsing scene plan JSON: {e}")
        return {"overall_status": f"Scene plan creation failed: {e}. "}
```

**Problem**: LLMs often return JSON wrapped in markdown code blocks or with explanatory text:
```
Here's the scene plan:
```json
{
  "scenes": [...]
}
```
```

This causes `json.loads()` to fail, and the node returns an error status instead of data.

### 2. **Exception Handling in Backend**

In `backend/main.py` (lines 1365-1500), the production pack generation has a try/catch that falls back to dummy data:

```python
try:
    # Call production pipeline nodes
    scene_result = await asyncio.to_thread(scene_breakdown_node, state)
    state.update(scene_result)
    
    if not state.get("scene_plan"):
        raise ValueError("Scene breakdown failed")  # ❌ Triggers fallback
    
    # ... more nodes ...
    
except Exception as prod_error:
    print(f"⚠ Production pipeline error: {prod_error}")
    # Fallback production pack with dummy data
    project["productionPack"] = {
        "budget": {"total_min": 15000.0, ...},  # ❌ DUMMY DATA
        ...
    }
```

**Problem**: When any node fails (due to JSON parsing), the entire production pack falls back to hardcoded dummy data.

### 3. **No Tavily Search Usage**

The production pipeline does **NOT** use Tavily search API. It only uses TAMUS LLM calls:
- ✅ Uses: `call_tamus_api()` for all nodes
- ❌ Does NOT use: Tavily search, web scraping, or external data sources

This is actually **correct** - production planning doesn't need web search. The issue is purely JSON parsing.

## Why This Happens

### Sequence of Failures:

1. **Scene Breakdown Node** calls TAMUS with prompt asking for JSON
2. **TAMUS returns** JSON wrapped in markdown or with extra text
3. **`json.loads()` fails** to parse the response
4. **Node returns** error status instead of data
5. **Backend checks** `if not state.get("scene_plan")` → True (no data)
6. **Exception raised** → "Scene breakdown failed"
7. **Fallback triggered** → Dummy data used
8. **UI displays** empty/zero values

## Evidence from Logs

When production pack generation runs, you'll see:
```
Running Production Pipeline
Scenes: 6
1. Generating scene breakdown...
Error parsing scene plan JSON: Expecting value: line 1 column 1 (char 0)
⚠ Production pipeline error: Scene breakdown failed
Using fallback production pack
✓ Using fallback production pack
```

## Solutions

### Option 1: Robust JSON Parsing (Recommended)

Add JSON extraction logic to handle LLM responses:

```python
def extract_json_from_llm_response(text: str) -> str:
    """Extract JSON from LLM response that may contain markdown or extra text."""
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    
    # Find JSON object or array
    json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    return text
```

### Option 2: Structured Output (Better)

Use TAMUS structured output mode if available:

```python
response = llm.messages().create(
    model=os.getenv("TAMUS_MODEL", "protected.gpt-5.2"),
    messages=[{"role": "user", "content": prompt}],
    response_format={"type": "json_object"},  # Force JSON output
    max_tokens=2000
)
```

### Option 3: Fallback to Text Parsing

If JSON fails, parse the text response and construct the data structure:

```python
try:
    scene_plan = json.loads(scene_plan_json)
except json.JSONDecodeError:
    # Parse text response and construct JSON manually
    scene_plan = parse_scene_plan_from_text(scene_plan_json)
```

### Option 4: Better Error Handling

Don't fall back to dummy data - return partial results:

```python
except Exception as prod_error:
    print(f"⚠ Production pipeline error: {prod_error}")
    # Use whatever data we got, even if incomplete
    project["productionPack"] = {
        "scenePlan": state.get("scene_plan", {}),
        "budget": state.get("budget_estimate", {}),
        # ... use actual data even if some nodes failed
    }
```

## Recommended Fix

Implement **Option 1 + Option 4**:
1. Add robust JSON extraction to `ad_production_pipeline.py`
2. Update error handling in `backend/main.py` to use partial results
3. Add better logging to identify which nodes are failing

This will ensure:
- ✅ LLM responses are parsed correctly even with markdown
- ✅ Partial results are shown instead of dummy data
- ✅ Users see real data even if some nodes fail
- ✅ Better debugging information in logs

## Files to Modify

1. **`ad_production_pipeline.py`**:
   - Add `extract_json_from_llm_response()` helper
   - Update all nodes to use robust JSON parsing
   - Add fallback text parsing for each node

2. **`backend/main.py`** (lines 1365-1500):
   - Update exception handling to use partial results
   - Add better logging for debugging
   - Remove hardcoded dummy data fallback

## Testing Plan

1. Run production pack generation with logging enabled
2. Check which nodes are failing and why
3. Verify JSON extraction works for various LLM response formats
4. Confirm UI shows real data instead of zeros
5. Test with incomplete data (some nodes failing)
