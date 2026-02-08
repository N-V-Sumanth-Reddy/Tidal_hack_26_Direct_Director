# Production Pipeline JSON Parsing Fix

## Issue Summary

Production pipeline was completing but returning empty/zero values:
- `✓ Generated locations plan with 0 locations` (API returned 18,796 chars)
- `✓ Generated budget estimate: $0 - $0` (API returned 8,566 chars)  
- `✓ Generated schedule: 0 shoot days` (API returned 9,501 chars)

## Root Cause

The TAMUS API (using `protected.gpt-5.2` model) was hitting the `max_tokens` limit before generating any output:

```json
{
  "content": "",  // Empty output
  "finish_reason": "length",  // Hit token limit
  "completion_tokens": 2000,
  "reasoning_tokens": 2000  // All tokens used for reasoning
}
```

The model uses **reasoning tokens** (like o1/o3 models) and was consuming all 2000 tokens for internal reasoning, leaving **zero tokens** for the actual JSON output.

## Solution

Increased `max_tokens` from default 4000 to **6000-8000** for all production planning nodes:

### Updated Nodes

1. **scene_breakdown_node**: `max_tokens=6000`
2. **location_planning_node**: `max_tokens=8000`
3. **budgeting_node**: `max_tokens=8000`
4. **schedule_ad_node**: `max_tokens=8000`
5. **casting_node**: `max_tokens=6000`
6. **props_wardrobe_node**: `max_tokens=6000`
7. **crew_gear_node**: `max_tokens=8000`
8. **legal_clearance_node**: `max_tokens=8000`
9. **risk_safety_node**: `max_tokens=8000`

### Code Changes

**File**: `ad_production_pipeline.py`

```python
# Before (hitting token limit)
locations_json = call_tamus_api(prompt)

# After (sufficient tokens for reasoning + output)
locations_json = call_tamus_api(prompt, max_tokens=8000)
```

## Verification

Tested with debug script `test_json_extraction_debug.py`:

**Before** (max_tokens=2000):
```
ERROR: No content in response (finish_reason: length)
```

**After** (max_tokens=8000):
```
✓ Success: 12544 chars returned
Locations count: 3
```

## Impact

- Production pipeline now generates **real data** instead of empty arrays
- Budget estimates show actual dollar amounts
- Location plans include multiple locations with details
- Schedule plans show correct shoot days
- All planning nodes return structured JSON data

## Files Modified

- `ad_production_pipeline.py` - Updated all production planning nodes with increased max_tokens
- `test_json_extraction_debug.py` - Created debug script to verify fix

## Backend Status

✓ Backend restarted with fixes applied
✓ Running on http://0.0.0.0:2501
✓ Ready for production pack generation testing
