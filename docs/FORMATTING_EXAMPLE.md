# Output Formatting - Before & After Example

## Problem: Raw LLM Output (Before)

This is what the user was seeing - unformatted, hard-to-read LLM output:

```
# GreenPhone - Sustainable Innovation Campaign

## Core Idea

Showcase the GreenPhone's eco-friendly features through a journey of transformation, highlighting how sustainable choices create a better future for everyone.

## 30-Second Story Beats

**0:00-0:05 | Opening Hook**
Close-up of hands holding a sleek GreenPhone against a backdrop of lush greenery. Sunlight filters through leaves, creating a natural, premium aesthetic.

**0:06-0:12 | Problem Setup**
Quick cuts showing environmental waste from traditional phone production - factory emissions, e-waste piles. Somber music.

[... continues with mixed formatting, inconsistent structure ...]
```

**Issues:**
- Mixed formatting styles
- Inconsistent structure
- Hard to parse visually
- No clear separation of sections
- Difficult to extract specific information

---

## Solution: Parsed & Formatted Output (After)

The output formatter parses the raw text and produces clean, structured markdown:

```markdown
# GreenPhone - Sustainable Innovation Campaign

## Core Idea

Showcase the GreenPhone's eco-friendly features through a journey of transformation, 
highlighting how sustainable choices create a better future for everyone.

## Story Beats

**0:00-0:05 | Opening Hook**

Close-up of hands holding a sleek GreenPhone against a backdrop of lush greenery. 
Sunlight filters through leaves, creating a natural, premium aesthetic.

**0:06-0:12 | Problem Setup**

Quick cuts showing environmental waste from traditional phone production - factory 
emissions, e-waste piles. Somber music.

**0:13-0:20 | Solution Reveal**

The GreenPhone emerges from recycled materials in a beautiful transformation sequence. 
Uplifting music begins.

## Why This Works

1. Emotional Appeal: Connects sustainability with personal responsibility and hope

2. Visual Storytelling: Uses transformation metaphor to show positive change

3. Clear Benefits: Demonstrates concrete eco-friendly features

4. Premium Positioning: Maintains aspirational brand image while being sustainable

## Visual & Sound Direction

**Palette:** Deep teal, warm gold light shafts, charcoal shadows, vibrant green accents

**Cinematography:** Smooth camera movements, macro shots of materials, wide establishing shots of nature

**Sound:** Ambient nature sounds transitioning to uplifting orchestral score

## Key Message

*"Sustainable innovation meets premium design - choose the future you want to see"*
```

**Benefits:**
- ✅ Consistent formatting throughout
- ✅ Clear section hierarchy
- ✅ Easy to read and scan
- ✅ Proper markdown structure
- ✅ Professional presentation
- ✅ Structured data available for programmatic access

---

## Screenplay Formatting Example

### Before (Raw LLM Output)
```
Scene 1 (5s)
Visual: Extreme close-up of GreenPhone in hand, sunlight creating lens flare through leaves
Action: Slow rotation of phone revealing sleek design and eco-friendly materials
Camera: Macro lens with shallow depth of field, slow push-in
Dialogue: (Voiceover) "Every choice shapes our world"
Text on Screen: "GreenPhone"

Scene 2 (5s)
Visual: Dark factory setting with smoke stacks, piles of electronic waste
Action: Time-lapse of waste accumulating, environmental degradation
Camera: Wide establishing shot, slow zoom out revealing scale
Dialogue: (Voiceover) "But what if we chose differently?"
```

### After (Parsed & Formatted)
```markdown
# GreenPhone - Sustainable Journey

**Genre:** Inspirational Drama

**Total Duration:** 30 seconds

---

## Scene 1 (5s)

**Visuals:** Extreme close-up of GreenPhone in hand, sunlight creating lens flare through leaves

**Action:** Slow rotation of phone revealing sleek design and eco-friendly materials

**Camera:** Macro lens with shallow depth of field, slow push-in

**Dialogue:** (Voiceover) "Every choice shapes our world"

**Text on Screen:** "GreenPhone"

---

## Scene 2 (5s)

**Visuals:** Dark factory setting with smoke stacks, piles of electronic waste

**Action:** Time-lapse of waste accumulating, environmental degradation

**Camera:** Wide establishing shot, slow zoom out revealing scale

**Dialogue:** (Voiceover) "But what if we chose differently?"

---
```

**Additional Benefits:**
- ✅ Each field is extracted and available separately
- ✅ Can be used programmatically (visual, action, camera, dialogue, text_on_screen)
- ✅ Consistent formatting across all scenes
- ✅ Clear visual hierarchy
- ✅ Professional screenplay format

---

## Technical Implementation

### Pydantic Models
```python
class ConceptOutput(BaseModel):
    title: str
    core_idea: str
    story_beats: List[Dict[str, str]]
    why_it_works: List[str]
    visual_direction: Dict[str, str]
    key_message: str

class SceneOutput(BaseModel):
    scene_number: int
    duration: int
    visuals: str
    action: str
    camera: Optional[str]
    dialogue: Optional[str]
    text_on_screen: Optional[str]
```

### Usage in Backend
```python
# Parse raw LLM output
parsed_concept = parse_concept(raw_llm_text)

# Format for display
formatted_text = format_concept_for_display(parsed_concept)

# Store both versions
project["concept"] = {
    "description": formatted_text,      # Clean formatted version
    "rawDescription": raw_llm_text,     # Original for reference
    # ... other fields
}
```

---

## Result

Users now see clean, professional, well-formatted content instead of raw LLM output. The system maintains both versions (formatted for display, raw for reference) and gracefully falls back to raw output if parsing fails.
