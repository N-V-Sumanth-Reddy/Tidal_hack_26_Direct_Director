# Storyboard Image Generation Prompts - Detailed Explanation

## Two-Stage Process

### Stage 1: LLM Agent Generates Detailed Prompts (TAMUS GPT-5.2)

The backend uses an LLM agent to create HIGH-QUALITY detailed prompts with character consistency.

**Agent Prompt Template:**
```
You are a professional storyboard artist creating detailed image generation prompts for a {BRAND} advertisement.

SCREENPLAY:
{Full screenplay with all scenes, descriptions, visuals, actions, camera, dialogue}

TASK:
Create detailed, cinematic image prompts for each scene that will generate high-quality advertising storyboard frames.

1. Define ONE MAIN CHARACTER with specific details:
   - Age, ethnicity, gender
   - Hair style and color  
   - Facial features (stubble, expression)
   - Build/physique
   - Clothing (be VERY specific - colors, style, fit)
   
2. For EACH scene, create a DETAILED prompt (300-500 words) including:
   - "Cinematic 16:9 storyboard frame" at the start
   - Color palette and lighting (be specific: "deep teal, warm gold light shafts, charcoal shadows")
   - Setting details (materials, atmosphere, mood)
   - **Character description in bold** - USE THE EXACT SAME CHARACTER IN ALL SCENES
   - Character's action and expression
   - Camera angle and movement (top-down, push-in, 360° orbit, etc.)
   - Close-up emphasis on specific details
   - Any text on screen
   - Justification cues: relatable moment, emotional appeal, clear message, premium aesthetics

3. Return as JSON array:
[
  {
    "scene_number": 1,
    "image_prompt": "Cinematic 16:9 storyboard frame... **Main character: [detailed description]**... [rest of detailed prompt]"
  }
]

CRITICAL REQUIREMENTS:
- Use the EXACT SAME character description (in bold **like this**) in EVERY scene
- Include specific color palette (e.g., "deep teal, warm gold, charcoal")
- Describe camera movements (push-in, orbit, whip-pan, etc.)
- Add close-up emphasis on key details
- Include "Justification cues:" at the end
- Make prompts 300-500 words each for maximum quality
- Return ONLY valid JSON, no other text
```

**LLM Response Example (JSON):**
```json
[
  {
    "scene_number": 1,
    "image_prompt": "Cinematic 16:9 storyboard frame in an epic tech-fantasy advertising style, consistent moody color palette (deep teal, warm gold light shafts, charcoal shadows), set in a dim temple-like workshop. A stone table centered in frame with a sleek, minimalist phone box labeled subtly \"GreenPhone\" (no other brands). Dust motes float through sanctum-like god rays from above. **GreenPhone protagonist: a 28-year-old South Asian male with short black hair, light stubble, athletic build, wearing a dark charcoal fitted hoodie and dark jeans** stands at the table, calm and principled, placing his palm gently on the box—stillness before a storm. Beside him is Maya (26, South Asian, sharp skeptical expression), arms folded, watching. Camera feeling: top-down angle transitioning into a slow push-in (show slight perspective shift, as if the camera is descending and moving closer). Close-up emphasis within the same frame: the protagonist's fingers lifting the lid, but the lid rises upward unnaturally as if time is pulling it (subtle reverse-motion aura, faint chrono-distortion shimmer). Atmosphere suggests a bassy war-drum \"thump\" via visual tension and vibrating dust motes. On-screen text integrated cleanly in lower third: **\"Reverse Unboxing.\"** Justification cues: relatable \"unboxing moment,\" emotional intrigue and anticipation, clear message of something different and purposeful, premium visual aesthetics."
  },
  {
    "scene_number": 2,
    "image_prompt": "Cinematic 16:9, same temple-workshop setting and lighting, same teal/gold palette and dust-filled sanctum rays. **GreenPhone protagonist: a 28-year-old South Asian male with short black hair, light stubble, athletic build, wearing a dark charcoal fitted hoodie and dark jeans** stands steady at the stone table, focused upward. The phone (ECOX/GreenPhone) floats above the open box; screws spin out by themselves, and modular components separate in midair—camera module, battery module, screen module—arranged like a sacred mechanical constellation. Add faint glowing symbols/runes etched on each module (subtle, not mystical overload—tech-mythic). Maya stands slightly behind, skepticism softening into awe. Camera look: a 360° orbit implied by a dynamic angled composition, with circular match-cut feeling (rings of motion blur arcs around the modules). Close-up detail visible on the phone frame: a crisp micro-stamp reading **\"TRACEABLE METALS.\"** On-screen text in clean modern type, mid-lower area: **\"Designed to repair. Built to last.\"** Justification cues: clear sustainability claim made tangible (repairable modularity), emotional shift from doubt to belief, sleek product-forward aesthetics."
  }
]
```

---

### Stage 2: Gemini Generates Images from Prompts

Each detailed prompt from the LLM is sent to **Gemini 2.5 Flash Image** model.

**Gemini API Call:**
```python
response = gemini_client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=image_prompt  # The 300-500 word detailed prompt from LLM
)
```

**Example Prompt Sent to Gemini (Scene 1):**
```
Cinematic 16:9 storyboard frame in an epic tech-fantasy advertising style, consistent moody color palette (deep teal, warm gold light shafts, charcoal shadows), set in a dim temple-like workshop. A stone table centered in frame with a sleek, minimalist phone box labeled subtly "GreenPhone" (no other brands). Dust motes float through sanctum-like god rays from above. **GreenPhone protagonist: a 28-year-old South Asian male with short black hair, light stubble, athletic build, wearing a dark charcoal fitted hoodie and dark jeans** stands at the table, calm and principled, placing his palm gently on the box—stillness before a storm. Beside him is Maya (26, South Asian, sharp skeptical expression), arms folded, watching. Camera feeling: top-down angle transitioning into a slow push-in (show slight perspective shift, as if the camera is descending and moving closer). Close-up emphasis within the same frame: the protagonist's fingers lifting the lid, but the lid rises upward unnaturally as if time is pulling it (subtle reverse-motion aura, faint chrono-distortion shimmer). Atmosphere suggests a bassy war-drum "thump" via visual tension and vibrating dust motes. On-screen text integrated cleanly in lower third: **"Reverse Unboxing."** Justification cues: relatable "unboxing moment," emotional intrigue and anticipation, clear message of something different and purposeful, premium visual aesthetics.
```

**Fallback Prompt (if LLM fails):**
```
Generate a professional storyboard frame for an advertisement.

Scene {scene_number}: {scene_description}

Style: Cinematic, professional advertising quality, detailed composition, 16:9 aspect ratio, high quality, photorealistic.
```

**Ultra-Simple Retry Prompt (if Gemini blocks content):**
```
Professional advertising photo: {first 100 chars of visual description}. Clean, modern style. 16:9 format.
```

---

## Key Features

### Character Consistency
- LLM defines ONE character at the start
- Same character description (in bold) appears in ALL scene prompts
- Example: **"GreenPhone protagonist: a 28-year-old South Asian male with short black hair, light stubble, athletic build, wearing a dark charcoal fitted hoodie and dark jeans"**

### Prompt Quality (300-500 words each)
- Specific color palette: "deep teal, warm gold light shafts, charcoal shadows"
- Camera movements: "top-down angle transitioning into a slow push-in"
- Close-up emphasis: "protagonist's fingers lifting the lid"
- Justification cues: "relatable moment, emotional appeal, clear message"

### Error Handling
1. **First attempt**: Use LLM-generated detailed prompt (300-500 words)
2. **If blocked**: Retry with ultra-simple prompt (< 50 words)
3. **If still fails**: Continue without image for that scene

### Safety Filter Handling
- Gemini may block prompts with `SAFETY` or `BLOCKED` finish reasons
- Retry logic automatically simplifies prompts to avoid blocks
- Logs show which scenes were blocked and retried

---

## Reference Quality

See `output/storyboard/storyboard_detailed.md` for examples of successful high-quality prompts that generated the reference images in `output/storyboard/scene_*.png`.

All 6 scenes in that reference used the same character description and maintained visual consistency across the entire storyboard.
