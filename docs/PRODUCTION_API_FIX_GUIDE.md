# Production API Error Fix Guide

## Problem Summary

The production pipeline is experiencing **TAMUS API empty response errors**. The API returns HTTP 200 (success) but with empty response bodies, resulting in production packs with all zeros:
- 0 scenes
- $0 budget
- 0 shoot days
- 0 locations

## Root Causes Identified

1. **API Rate Limiting**: The production pipeline runs 6 nodes in parallel, potentially overwhelming the TAMUS API
2. **Request Payload Size**: Some prompts may be too long (>10,000 characters)
3. **API Quota/Service Issues**: The API may be rate-limited or experiencing service issues

## Fixes Applied

### 1. Sequential Execution with Delays (backend/main.py)
**Changed**: Production nodes now run sequentially with 3-second delays between each API call
**Why**: Prevents overwhelming the API with parallel requests
**Impact**: Production generation will take ~18 seconds longer, but should succeed

### 2. Enhanced Error Logging (tamus_wrapper.py)
**Added**: Detailed diagnostics for API responses
- Response body length
- Empty response detection
- Request details logging
**Why**: Better visibility into what's failing
**Impact**: Easier debugging of API issues

### 3. Prompt Length Management (ad_production_pipeline.py)
**Added**: 
- Prompt length warnings (>10,000 chars)
- Automatic truncation for extremely long prompts (>15,000 chars)
- Increased retry backoff (3s, 6s, 9s instead of 2s, 4s, 6s)
**Why**: Prevents API failures due to oversized requests
**Impact**: More reliable API calls

### 4. Configurable Rate Limiting (.env)
**Added**: `TAMUS_API_DELAY=3` environment variable
**Why**: Allows tuning the delay between API calls
**Impact**: Can adjust if 3 seconds isn't enough

## Testing the Fix

### Step 1: Run Diagnostic Tests
```bash
cd /path/to/project
python test_tamus_api.py
```

This will test:
1. Simple API request (basic connectivity)
2. JSON generation (production-style request)
3. Production prompt (scene breakdown simulation)

**Expected Output**: All 3 tests should pass

### Step 2: Test Production Pipeline
1. Start backend: `cd backend && python main.py`
2. Start frontend: `cd virtual-ad-agency-ui && npm run dev`
3. Create a new project
4. Submit a brief
5. Generate concept and screenplays
6. Generate storyboard
7. **Generate production pack** (this is where errors occurred)

**Watch the backend logs** for:
- `[TAMUS] Prompt length:` - Should be <15,000 chars
- `[TAMUS] ✓ Success:` - Should see this for each node
- `✓ Production pack generated successfully` - Final success message

## If Issues Persist

### Check 1: API Key Validity
```bash
# Check if API key is set
echo $TAMUS_API_KEY

# Or check .env file
cat .env | grep TAMUS_API_KEY
```

### Check 2: API Quota
Contact your TAMU administrator to check:
- API quota remaining
- Rate limit settings
- Any service alerts

### Check 3: Increase Delays
If still getting empty responses, increase the delay:

**In .env**:
```bash
TAMUS_API_DELAY=5  # Increase from 3 to 5 seconds
```

**In backend/main.py** (lines 1390-1420):
```python
await asyncio.sleep(5)  # Change all from 3 to 5
```

### Check 4: Simplify Prompts
If prompts are too complex, you can simplify them in `ad_production_pipeline.py`:
- Reduce the number of requirements in each prompt
- Remove detailed examples
- Focus on essential fields only

## Alternative Solutions

### Option 1: Use Mock Data (Temporary)
If the API continues to fail, you can temporarily use mock data for testing:

**In backend/main.py**, add this at the top of the production section:
```python
# TEMPORARY: Use mock data if API fails
USE_MOCK_PRODUCTION = os.getenv("USE_MOCK_PRODUCTION", "false").lower() == "true"
```

### Option 2: Switch to Different LLM
If TAMUS API is unreliable, consider:
- Using Gemini API for text generation (not just images)
- Using OpenAI API
- Using Anthropic Claude API

## Monitoring

### Backend Logs to Watch
```bash
# Good signs:
[TAMUS] ✓ Success: 1234 chars returned
✓ Generated scene plan with 6 scenes
✓ Production pack generated successfully

# Bad signs:
[TAMUS] ⚠ Empty response body
✗ TAMUS API failed after 3 attempts
⚠ Production pipeline error
```

### Frontend Indicators
- Production pack should show non-zero values
- Budget should be in range $30,000 - $80,000
- Shoot days should be 1-3
- Locations should be 2-5

## Known Issues

### Issue 1: Gemini API Key Leaked
**Status**: Separate issue, affects storyboard images only
**Fix**: Get new API key from https://makersuite.google.com/app/apikey
**Workaround**: System uses fallback images from `output/storyboard/` folder

### Issue 2: TAMUS API Empty Responses
**Status**: Fixed with this update
**Fix**: Sequential execution + delays + better error handling
**Workaround**: Run diagnostic tests first

## Success Criteria

✅ All 3 diagnostic tests pass
✅ Production pack shows non-zero values
✅ Backend logs show successful API calls
✅ No empty response errors in logs
✅ Production generation completes in ~60-90 seconds

## Contact

If issues persist after trying all fixes:
1. Run `python test_tamus_api.py` and save the output
2. Check backend logs for detailed error messages
3. Contact TAMU API support with:
   - API key (first 10 characters only)
   - Error messages from logs
   - Diagnostic test results
   - Timestamp of failures

---

**Last Updated**: 2026-02-08
**Version**: 1.0
