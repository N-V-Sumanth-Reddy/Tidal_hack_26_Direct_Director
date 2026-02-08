# Gemini Image Response Parser Fix

## Issue Summary

Storyboard image generation was showing warnings and falling back to placeholder images for some scenes:

```
⚠ No inline_data in part
Using fallback image: output/storyboard/scene_1.png
```

Even though the API call succeeded (`finish_reason: STOP`), the parser couldn't extract the image data.

## Root Cause

The original parser had two problems:

1. **Only checked `parts[0]`**: Gemini responses can contain multiple parts (e.g., text part first, image part second). The code only checked the first part, missing images in later parts.

2. **Only looked for `inline_data`**: Some Gemini responses return images as:
   - `inline_data` (embedded bytes) ✓ Original code handled this
   - `file_data.file_uri` (URI reference) ✗ Original code missed this
   - Multiple parts with mixed content ✗ Original code missed this

## Solution

Updated the image extraction logic to:

1. **Scan ALL parts** (not just `parts[0]`)
2. **Handle multiple formats**:
   - `inline_data` with embedded bytes
   - `file_data` with URI references (logged for future implementation)
   - Text parts (logged and skipped)
3. **Detailed logging** to show which part contains the image

### Code Changes

**File**: `backend/main.py` (lines 970-1010)

**Before** (only checked parts[0]):
```python
part = candidate.content.parts[0]
if hasattr(part, 'inline_data') and part.inline_data is not None:
    # Extract image
else:
    print(f"  ⚠ No inline_data in part")
```

**After** (scans all parts):
```python
parts = candidate.content.parts
print(f"  Response has {len(parts)} part(s)")

for part_idx, part in enumerate(parts):
    # Method 1: inline_data (embedded bytes)
    if hasattr(part, 'inline_data') and part.inline_data is not None:
        if hasattr(part.inline_data, 'data') and part.inline_data.data is not None:
            image_bytes = part.inline_data.data
            mime_type = getattr(part.inline_data, 'mime_type', 'image/png')
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            image_url = f"data:{mime_type};base64,{image_base64}"
            print(f"  ✓ Image found in part[{part_idx}] (inline_data): {len(image_bytes)} bytes")
            break
    
    # Method 2: file_data (URI reference)
    if hasattr(part, 'file_data') and part.file_data is not None:
        if hasattr(part.file_data, 'file_uri'):
            file_uri = part.file_data.file_uri
            print(f"  ✓ Image found in part[{part_idx}] (file_uri): {file_uri}")
            # TODO: Download from URI if needed
    
    # Method 3: text part (no image)
    if hasattr(part, 'text') and part.text:
        print(f"  Part[{part_idx}] is text: {part.text[:100]}...")
```

## Expected Behavior After Fix

### Successful Image Generation
```
Processing scene 1/5...
  Generating image for scene 1...
  Finish reason: FinishReason.STOP
  Response has 2 part(s)
  Part[0] is text: Scene description...
  ✓ Image found in part[1] (inline_data): 45678 bytes
```

### Fallback (Only When Truly No Image)
```
Processing scene 2/5...
  Generating image for scene 2...
  Finish reason: FinishReason.STOP
  Response has 1 part(s)
  Part[0] is text: Unable to generate image...
  ⚠ No image data found in any of 1 part(s)
  Using fallback image: output/storyboard/scene_2.png
```

## Impact

- Correctly extracts images from multi-part Gemini responses
- Reduces unnecessary fallback to placeholder images
- Better logging for debugging image generation issues
- Prepared for future URI-based image responses

## Files Modified

- `backend/main.py` - Updated Gemini image response parser (lines 970-1010)

## Backend Status

✓ Backend restarted with fixes applied
✓ Running on http://0.0.0.0:2501
✓ Ready for storyboard generation testing

## Future Enhancements

- Implement URI download for `file_data.file_uri` responses
- Add retry logic for failed image extractions
- Cache successful image generation patterns
