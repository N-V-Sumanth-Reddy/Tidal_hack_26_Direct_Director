# Using the Output Formatter

## Overview

The output formatter automatically parses and formats raw LLM outputs into clean, structured, readable content. It's now integrated into the backend generation pipeline and works automatically.

## How It Works

### Automatic Processing

When you generate content through the API, the formatter automatically:

1. **Parses** raw LLM output into structured data
2. **Formats** it into clean markdown
3. **Stores** both formatted and raw versions
4. **Falls back** to raw output if parsing fails

No configuration needed - it just works!

## What Gets Formatted

### 1. Concepts
- **Title** - Extracted and cleaned
- **Core Idea** - Formatted with proper spacing
- **Story Beats** - Structured with timing and descriptions
- **Why It Works** - Numbered list of justification points
- **Visual Direction** - Organized by category (palette, cinematography, sound)
- **Key Message** - Highlighted and emphasized

### 2. Screenplays
- **Scenes** - Structured with all fields extracted:
  - Scene number and duration
  - Visuals description
  - Action description
  - Camera direction
  - Dialogue
  - Text on screen
- **Metadata** - Genre, setting, total duration
- **Formatting** - Professional screenplay format

## Accessing Formatted Content

### In the API Response

#### Concept
```json
{
  "concept": {
    "description": "Clean formatted markdown",  // Use this for display
    "rawDescription": "Raw LLM output",        // Original for reference
    "title": "Parsed title",
    // ... other fields
  }
}
```

#### Screenplay
```json
{
  "screenplays": [
    {
      "formattedText": "Clean formatted screenplay",  // Use this for display
      "rawText": "Raw LLM output",                   // Original for reference
      "scenes": [
        {
          "description": "Combined description",
          "visual": "Visual details",        // Individual fields available
          "action": "Action details",
          "camera": "Camera direction",
          "dialogue": "Dialogue text",
          "text_on_screen": "On-screen text"
        }
      ]
    }
  ]
}
```

## Frontend Display

### Current Behavior
The frontend already displays the formatted content automatically:
- `ConceptStep.tsx` shows `concept.description` (now formatted)
- `ScreenplayCompare.tsx` shows scene descriptions (now structured)

### Optional Enhancements

You can enhance the frontend to take advantage of the structured data:

#### 1. Show Full Formatted Screenplay
```tsx
// Add a button to view full formatted screenplay
<button onClick={() => showFormattedScreenplay(screenplay.formattedText)}>
  View Full Screenplay
</button>
```

#### 2. Display Individual Scene Fields
```tsx
// Show structured scene data
<div className="scene">
  <h3>Scene {scene.sceneNumber}</h3>
  
  {scene.visual && (
    <div className="scene-field">
      <strong>Visuals:</strong> {scene.visual}
    </div>
  )}
  
  {scene.action && (
    <div className="scene-field">
      <strong>Action:</strong> {scene.action}
    </div>
  )}
  
  {scene.camera && (
    <div className="scene-field">
      <strong>Camera:</strong> {scene.camera}
    </div>
  )}
  
  {scene.dialogue && (
    <div className="scene-field">
      <strong>Dialogue:</strong> {scene.dialogue}
    </div>
  )}
</div>
```

#### 3. Toggle Between Formatted and Raw
```tsx
const [showRaw, setShowRaw] = useState(false);

<button onClick={() => setShowRaw(!showRaw)}>
  {showRaw ? 'Show Formatted' : 'Show Raw'}
</button>

<div>
  {showRaw ? concept.rawDescription : concept.description}
</div>
```

## Testing

### Run the Test Suite
```bash
cd backend
python test_output_formatter_integration.py
```

This will verify:
- ✓ Concept parsing works
- ✓ Screenplay parsing works
- ✓ Formatting produces clean output
- ✓ All fields are extracted correctly

### Manual Testing

1. Start the backend:
   ```bash
   cd backend
   python main.py
   ```

2. Create a project and generate content through the UI

3. Check the API response - you should see:
   - `concept.description` with clean formatted markdown
   - `concept.rawDescription` with original LLM output
   - `screenplay.formattedText` with clean formatted screenplay
   - `screenplay.rawText` with original LLM output

## Troubleshooting

### Formatter Not Working?

Check the backend logs for:
```
✓ Successfully imported output formatter
```

If you see this, the formatter is loaded correctly.

### Seeing Raw Output Instead of Formatted?

The formatter has graceful fallback - if parsing fails, it uses raw output. Check logs for:
```
⚠ Concept formatting failed: [error], using raw output
```

This means the LLM output format was unexpected. The raw output will still be displayed.

### Want to Customize Formatting?

Edit `backend/output_formatter.py`:
- Modify `parse_concept()` to adjust concept parsing
- Modify `parse_screenplay()` to adjust screenplay parsing
- Modify `format_*_for_display()` to change output format

## Benefits

✅ **Clean Display** - No more raw LLM text
✅ **Structured Data** - All fields extracted and available
✅ **Professional Format** - Consistent markdown formatting
✅ **Backward Compatible** - Raw output preserved for reference
✅ **Graceful Degradation** - Falls back to raw if parsing fails
✅ **Zero Configuration** - Works automatically

## Next Steps

1. ✅ **Backend Integration** - Complete (this is done)
2. ⏭️ **Frontend Enhancement** - Optional (add formatted text display)
3. ⏭️ **Custom Formatting** - Optional (adjust formatting rules)
4. ⏭️ **Additional Fields** - Optional (parse more LLM output fields)

The formatter is ready to use and will automatically improve the display of all LLM-generated content!
