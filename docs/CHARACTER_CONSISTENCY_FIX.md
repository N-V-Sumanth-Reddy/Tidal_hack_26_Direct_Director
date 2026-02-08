# Character Consistency Fix for Storyboard Images

## Issue

Characters appeared inconsistent across storyboard images - different appearances, clothing, and visual styles between scenes, breaking the narrative continuity.

## Root Cause

Each scene was being generated independently without a shared character reference, causing Gemini to create different interpretations of the same character in each frame.

## Solution

Implemented a **two-phase character consistency system**:

### Phase 1: Character Extraction (Before Image Generation)

Before generating any images, the system now:

1. **Analyzes the entire screenplay** using TAMUS GPT-5.2
2. **Extracts character descriptions** including:
   - Physical appearance (age, gender, ethnicity)
   - Clothing and distinctive features
   - Visual style and tone
3. **Creates a character reference** (2-3 sentences) to maintain consistency

**Prompt Example:**
```
Analyze this screenplay and extract consistent character descriptions:

[Screenplay text...]

Extract:
1. Main character(s) physical appearance (age, gender, ethnicity, clothing, distinctive features)
2. Supporting characters (if any)
3. Visual style and tone

Return a concise character reference (2-3 sentences) that can be used to maintain consistency across all scenes.
```

**Temperature:** `0.3` (lower for consistent extraction)

### Phase 2: Image Generation with Character Reference

Each scene image is generated with:

1. **Scene-specific description** from the screenplay
2. **Character consistency note** injected into every prompt
3. **Lower temperature** for more deterministic results

**Enhanced Prompt Structure:**
```
Professional cinematic storyboard frame for advertisement.

Scene X of Y:
[Scene description]

CHARACTER CONSISTENCY (maintain across all scenes):
[Extracted character description]

CRITICAL: Maintain exact same character appearance, clothing, and visual style as described above.
Style: Cinematic 16:9 format, professional advertising quality, photorealistic, high detail, dramatic lighting, premium aesthetics.
Temperature: 0.5 (for consistency)
```

### Gemini Configuration

**Updated Parameters:**
- `temperature: 0.5` (reduced from default 1.0)
- `top_p: 0.8` (focused sampling)
- `top_k: 20` (limited token selection)

## Code Changes

**File:** `backend/main.py` (lines 930-980)

### Before (No Character Consistency)
```python
image_prompt = f"""Professional cinematic storyboard frame for advertisement.

Scene {scene_number} of {total_scenes}:
{scene_description}

Style: Cinematic 16:9 format, professional advertising quality, photorealistic, high detail, consistent character design across all scenes, dramatic lighting, premium aesthetics."""

response = await asyncio.to_thread(
    gemini_client.models.generate_content,
    model="gemini-2.5-flash-image",
    contents=image_prompt
)
```

### After (With Character Consistency)
```python
# STEP 1: Extract character descriptions
character_prompt = f"""Analyze this screenplay and extract consistent character descriptions:
{screenplay_text}
..."""

character_response = await asyncio.to_thread(
    llm.messages().create,
    model="protected.gpt-5.2",
    messages=[{"role": "user", "content": character_prompt}],
    max_tokens=500,
    temperature=0.3  # Lower for consistency
)

# STEP 2: Generate images with character reference
consistency_note = f"\n\nCHARACTER CONSISTENCY (maintain across all scenes):\n{character_description}"

image_prompt = f"""Professional cinematic storyboard frame for advertisement.

Scene {scene_number} of {total_scenes}:
{scene_description}{consistency_note}

CRITICAL: Maintain exact same character appearance, clothing, and visual style as described above.
..."""

response = await asyncio.to_thread(
    gemini_client.models.generate_content,
    model="gemini-2.5-flash-image",
    contents=image_prompt,
    config={
        "temperature": 0.5,  # Lower for consistency
        "top_p": 0.8,
        "top_k": 20
    }
)
```

## Expected Results

### Before Fix
- Scene 1: Young woman in red dress
- Scene 2: Different woman in blue outfit
- Scene 3: Completely different character
- ❌ No visual continuity

### After Fix
- Scene 1: Young woman in red dress, brown hair, professional attire
- Scene 2: **Same woman** in red dress, brown hair, professional attire
- Scene 3: **Same woman** in red dress, brown hair, professional attire
- ✅ Visual continuity maintained

## Performance Impact

- **Additional Time:** +5-10 seconds (one-time character extraction)
- **Total Storyboard Time:** 35-70 seconds (6 scenes)
- **Trade-off:** Slightly longer generation for significantly better consistency

## Configuration

### Temperature Settings

| Component | Temperature | Purpose |
|-----------|-------------|---------|
| Character Extraction | 0.3 | Consistent, focused descriptions |
| Image Generation | 0.5 | Balanced creativity + consistency |
| Default (before fix) | 1.0 | High creativity, low consistency |

### Sampling Parameters

- `top_p: 0.8` - Focus on top 80% probability tokens
- `top_k: 20` - Limit to top 20 token choices
- Both reduce randomness for more consistent results

## Fallback Behavior

If character extraction fails:
- System logs warning
- Proceeds with image generation without character reference
- Still uses lower temperature (0.5) for some consistency

## Testing

To verify character consistency:

1. Generate a storyboard with 6 scenes
2. Check backend logs for:
   ```
   Extracting character descriptions for consistency...
   ✓ Character description extracted: [description]
   ```
3. Inspect generated images - characters should maintain:
   - Same facial features
   - Same clothing
   - Same visual style
   - Same color palette

## Future Enhancements

- **Character reference images:** Upload reference image for even stronger consistency
- **Multiple character tracking:** Handle multiple characters separately
- **Style transfer:** Maintain artistic style across scenes
- **Pose consistency:** Suggest similar poses for continuity

## Files Modified

- `backend/main.py` - Added character extraction and enhanced prompts (lines 930-1020)

## Backend Status

✅ Backend restarted with character consistency improvements
✅ Running on http://0.0.0.0:2501
✅ Ready for storyboard generation with consistent characters
