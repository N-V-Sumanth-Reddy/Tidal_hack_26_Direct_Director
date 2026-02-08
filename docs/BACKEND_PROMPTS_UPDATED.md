# Backend Prompts - Currently Updated in backend/main.py

This document shows the EXACT prompts currently being used in `backend/main.py` after my updates.

---

## 1. CONCEPT GENERATION PROMPT

**Location**: `backend/main.py` - Line ~200

```python
concept_prompt = f"""You are a creative director for advertising campaigns.

Brief:
- Platform: {brief.get('platform', 'YouTube')}
- Duration: {brief.get('duration', 30)} seconds
- Budget: ${brief.get('budget', 50000):,}
- Location: {brief.get('location', 'Studio')}
- Creative Direction: {brief.get('creativeDirection', '')}
- Brand: {', '.join(brief.get('brandMandatories', []))}
- Target Audience: {brief.get('targetAudience', '')}
- Constraints: {', '.join(brief.get('constraints', []))}

Generate a creative concept for this ad campaign. Include:
1. Core concept/theme
2. Key message
3. Visual style
4. Emotional tone
5. How it addresses the target audience

Be creative and specific."""
```

**Status**: ❌ **NOT using notebook prompt** - This is simplified

---

## 2. SCREENPLAY GENERATION - RAJAMOULI STYLE

**Location**: `backend/main.py` - Line ~280

```python
screenplay_prompt_a = f"""#Context: You are an autonomous AI screenplay creation agent designed to create a screenplay for any given advertisement concept.

#Objective: Generate a unique, fresh, and novel screenplay for an advertisement concept.

#Guidelines:

1. Style and Inspiration:
  - The screenplay should be influenced by the style of SS Rajamouli, a renowned Indian cinema director known for his epic storytelling, grand visuals, and emotional depth.
  - Emulate the cinematic experience seen in Rajamouli's films, focusing on strong character development, dramatic plot twists, and visually captivating scenes.

2. Content Compliance:
  - Ensure the screenplay adheres to all content guidelines and does not include any content violations.
  - Avoid themes or depictions that could be considered offensive, inappropriate, or culturally insensitive.

3. Screenplay Structure:
  - Title: [Provide a captivating title for the ad concept]
  - Genre: [Specify the genre, e.g., fantasy, action, drama, etc.]
  - Setting: Describe the primary locations and time periods where the story takes place.
  - Characters: Introduce the main characters, detailing their roles, personalities, and relationships.
  - Plot Overview: Provide a brief summary of the story arc, including the main conflict and resolution.
  - Scenes: Outline the key scenes in the screenplay, ensuring a logical flow and narrative progression.
  - Dialogue: Craft engaging and authentic dialogue that reflects the characters' personalities and advances the plot.

4. Scene Breakdown (MUST HAVE EXACTLY 5 SCENES):

  a. Opening Scene:
    - Visuals: Describe the setting, atmosphere, and key visual elements in DETAIL.
    - Action: Detail the actions and movements of characters within the scene.
    - Camera Transition: Specify camera angles, movements, and transitions.
    - Close-Up: Highlight any close-up shots that emphasize emotions or significant details.
    - Text on Screen: Include any text that appears on screen, such as titles, captions, or subtitles.

  b. Middle Scenes (Scenes 2-4):
    - Follow the same structure as the opening scene for each subsequent scene, ensuring continuity and coherence in the narrative.

  c. Ending Scene (Scene 5):
    - Resolve the main conflict, wrap up loose ends, and provide a satisfying conclusion.

Additional Notes:
  - STRICTLY RESTRICT THE SCREENPLAY WITH IN 3500 Characters.
  - Ensure the screenplay is engaging, emotionally resonant, and leaves a lasting impact on the audience.
  - Maintain the color palette, mood, and character consistency throughout the screenplay.
  - Incorporate Rajamouli's signature elements such as heroic feats, moral dilemmas, and visually stunning sequences.
  - MUST HAVE EXACTLY 5 SCENES with detailed visual descriptions.

Given Concept: {concept}
Duration: {brief.get('duration', 30)} seconds
Platform: {brief.get('platform', 'YouTube')}

Generate the complete screenplay now in RAJAMOULI STYLE with EXACTLY 5 SCENES."""
```

**Status**: ✅ **EXACT COPY from notebook**

---

## 3. SCREENPLAY GENERATION - SHANKAR STYLE

**Location**: `backend/main.py` - Line ~350

```python
screenplay_prompt_b = f"""#Context: You are an autonomous AI screenplay creation agent designed to create a screenplay for any given advertisement concept.

#Objective: Generate a unique, fresh, and novel screenplay for an advertisement concept.

#Guidelines:

1. Style and Inspiration:
  - The screenplay should be influenced by the style of Shankar, a renowned Indian cinema director known for his grandiose visuals, intricate storytelling, and socially relevant themes.
  - The screenplay should reflect Shankar's cinematic experience, including high-impact visuals, compelling narratives, and dramatic sequences. Emphasize strong character development, elaborate sets, and emotional depth.

2. Content Compliance:
  - Ensure the screenplay adheres to all content guidelines and does not include any content violations.
  - Avoid themes or depictions that could be considered offensive, inappropriate, or culturally insensitive.

3. Screenplay Structure:
  - Title: [Provide a captivating title for the ad concept]
  - Genre: [Specify the genre, e.g., fantasy, action, drama, etc.]
  - Setting: Describe the primary locations and time periods where the story takes place.
  - Characters: Introduce the main characters, detailing their roles, personalities, and relationships.
  - Plot Overview: Provide a brief summary of the story arc, including the main conflict and resolution.
  - Scenes: Outline the key scenes in the screenplay, ensuring a logical flow and narrative progression.
  - Dialogue: Craft engaging and authentic dialogue that reflects the characters' personalities and advances the plot.

4. Scene Breakdown (MUST HAVE EXACTLY 5 SCENES):

  a. Opening Scene:
    - Visuals: Describe the setting, atmosphere, and key visual elements in DETAIL.
    - Action: Detail the actions and movements of characters within the scene.
    - Camera Transition: Specify camera angles, movements, and transitions.
    - Close-Up: Highlight any close-up shots that emphasize emotions or significant details.
    - Text on Screen: Include any text that appears on screen, such as titles, captions, or subtitles.

  b. Middle Scenes (Scenes 2-4):
    - Follow the same structure as the opening scene for each subsequent scene, ensuring continuity and coherence in the narrative.

  c. Ending Scene (Scene 5):
    - Resolve the main conflict, wrap up loose ends, and provide a satisfying conclusion.

Additional Notes:
  - STRICTLY RESTRICT THE SCREENPLAY WITH IN 3500 Characters.
  - Ensure the screenplay is engaging, emotionally resonant, and leaves a lasting impact on the audience.
  - Maintain the color palette, mood, and character consistency throughout the screenplay.
  - Incorporate Shankar's signature elements such as grandiose visuals, intricate storytelling, and socially relevant themes.
  - MUST HAVE EXACTLY 5 SCENES with detailed visual descriptions.

Given Concept: {concept}
Duration: {brief.get('duration', 30)} seconds
Platform: {brief.get('platform', 'YouTube')}

Generate the complete screenplay now in SHANKAR STYLE with EXACTLY 5 SCENES."""
```

**Status**: ✅ **EXACT COPY from notebook**

---

## 4. STORYBOARD IMAGE GENERATION PROMPT

**Location**: `backend/main.py` - Line ~550

```python
image_prompt = f"""#Context: You are an autonomous AI image generation agent designed to create unique and high-quality images based on user-provided prompts. Your task is to interpret the given prompt creatively and generate an image that accurately reflects the described scene or concept.

#Objective: Generate a professional storyboard frame for advertisement Scene {scene_number} of {total_scenes}

#Scene Information:
- Scene Number: {scene_number}/{total_scenes}
- Duration: {scene_duration} seconds
- Full Description: {scene_description}

#Detailed Scene Elements:
- Visual Elements: {scene_visual if scene_visual else scene_description}
- Action/Movement: {scene_action if scene_action else "Dynamic scene progression"}
- Camera Work: {scene_camera if scene_camera else "Cinematic framing with professional composition"}
- Dialogue/Audio: {scene_dialogue if scene_dialogue else "Atmospheric sound design"}
- Text on Screen: {scene_text if scene_text else "None"}

#Image Generation Guidelines:

1. Visual Composition:
   - Focus on the main visual elements: setting, objects, characters
   - Capture the atmosphere and mood described
   - Use cinematic lighting and professional composition
   - 16:9 aspect ratio, high quality, photorealistic

2. Action and Motion:
   - Capture the described action with emphasis on motion or interaction
   - Show character movements and emotional expressions
   - Convey dynamic energy where applicable

3. Camera Work:
   - Reflect the specified camera angles and transitions
   - Use perspective to enhance storytelling
   - Create depth and visual interest

4. Consistency Requirements:
   - Maintain consistent color palette across all scenes
   - Keep character appearances consistent
   - Preserve mood and visual style throughout
   - Professional advertising quality

5. Style Requirements:
   - Cinematic quality with dramatic lighting
   - Clear visual storytelling
   - Emotionally engaging composition
   - Professional storyboard frame for advertisement

Generate a high-quality, professional storyboard image that captures all these elements."""
```

**Status**: ⚠️ **SIMILAR to notebook but NOT agent-based**

---

## KEY DIFFERENCES FROM NOTEBOOK

### What's CORRECT:
1. ✅ Screenplay prompts are EXACT copies from notebook
2. ✅ Scene breakdown structure is requested (Visual, Action, Camera, Close-Up, Text)
3. ✅ Using Gemini 2.5 Flash Image for generation

### What's MISSING:
1. ❌ **Agent-based approach**: Notebook uses LangChain agent with tools, we use direct API calls
2. ❌ **gen_id parameter**: For character consistency across images (DALL-E 3 specific)
3. ❌ **seed parameter**: For reproducibility (DALL-E 3 specific)
4. ❌ **Iterative processing**: Agent processes ALL scenes together, we process one-by-one
5. ❌ **Concept prompt**: Not using the notebook's simple prompt

### What's BROKEN:
1. ❌ **Scene parsing**: Not extracting structured fields (Visual, Action, Camera, etc.) properly
2. ❌ **Description quality**: Losing detail during parsing
3. ❌ **Image consistency**: No mechanism to maintain character/style consistency

---

## RECOMMENDED FIXES

### Option 1: Use Full LangGraph Pipeline (BEST)
Switch to `ad_production_pipeline_web.py` which has proper LangGraph implementation

### Option 2: Fix Current Implementation (QUICK)
1. Update concept prompt to match notebook
2. Fix scene parsing to extract all structured fields
3. Add character consistency instructions to image prompts
4. Add retry logic for failed images

### Option 3: Hybrid Approach (RECOMMENDED)
1. Keep current screenplay prompts (they're correct)
2. Fix scene parsing to preserve structure
3. Pass complete scene structure to image generation
4. Add explicit consistency instructions mentioning previous scenes

---

## NEXT STEPS

Which approach would you like me to implement?

1. **Switch to full pipeline** (`ad_production_pipeline_web.py`)
2. **Fix current implementation** with better parsing and consistency
3. **Hybrid approach** - fix parsing + improve prompts
