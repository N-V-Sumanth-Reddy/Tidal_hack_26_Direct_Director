# Implementation Plan: Use Exact Notebook Prompts & LangGraph Architecture

## Current Issues

1. **Only 1 out of 5 images generating** - Gemini blocking prompts
2. **Character inconsistency** - No gen_id/seed mechanism
3. **Missing scene structure** - Only generic "description" field
4. **Procedural approach** - Not using agent-based workflow

## Root Cause

The current backend implementation does NOT match the notebook's approach:

### Notebook Approach (CORRECT)
- Uses **LangGraph** with StateGraph
- **Agent-based** storyboard generation
- Passes **ENTIRE screenplay** to storyboard agent at once
- Agent has access to `generate_image` tool
- Uses **gen_id** and **seed** for consistency
- Structured scenes with: Visual, Sound, Camera, Action, Close-Up, Text

### Current Backend (INCORRECT)
- No LangGraph
- **Procedural** loop through scenes
- Processes scenes **one at a time**
- Manual prompt construction
- No gen_id/seed
- Only generic "description" field

## Solution: Implement Exact Notebook Architecture

### Step 1: Update Screenplay Prompts

Use the EXACT prompts from the notebook (already in backend):

```python
# Rajamouli Style - EXACT from notebook
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

✅ **This is already in the backend!**

### Step 2: Fix Scene Parsing

The current `parse_scenes()` function loses structure. Update it to preserve:
- Visual
- Action
- Camera Transition
- Close-Up
- Text on Screen
- Dialogue

✅ **This is already partially done** - the function extracts these fields but they're not being used properly.

### Step 3: Implement Storyboard Agent (CRITICAL)

This is the MAIN missing piece. The notebook uses an **agent-based approach**:

```python
story_board_image_generate_prompt = """#Context: You are an autonomous AI image generation agent designed to create unique and high-quality images based on user-provided prompts. Your task is to interpret the given prompt creatively and generate an image that accurately reflects the described scene or concept.

#Objective: Generate images for storyboard creation for advertisements by adhering to the below guidelines

#Guidelines:

1. Receive and Process Multi-Scene Prompts:
    - The prompt will contain multiple scenes.
    - Each scene will include the following components: Visual, Sound, Camera Transition, Action, Close-Up, Text on Screen.
    - Also the prompt consists of Justification with Relatability, Emotional Appeal, Visual Aesthetics, Clear Message.

2. Iterative Scene Processing:
    - For each scene, extract the Visual, Sound, Camera Transition, Action, Close-Up, and Text on Screen elements.
    - Generate an image that accurately represents the combined essence of these elements.
    - Ensure that you use the gen_id=yRmG5bW4bmcfWbVP across all the scenes
    - You must use the seed value=12345 across all the scenes

3. Image Generation Guidelines:
    - Visual: Focus on the main visual elements described. This includes the setting, objects, and characters.
    - Sound: Although sound is auditory, interpret and reflect the mood or atmosphere it conveys visually.
    - Camera Transition: Reflect the specified camera transitions (e.g., zoom, pan, tilt) to capture the dynamic aspect of the scene.
    - Action: Ensure the image captures the described action, emphasizing motion or interaction where applicable.
    - Close-Up: Highlight any specified close-up elements to focus on details or emotions.
    - Text on Screen: Integrate the provided text into the image, ensuring it complements the visual narrative.
    - Make sure you include the and follow Justification mentioned in Guidelines #1 in all the images that you generate

4. Consistency and Continuity:
    - Maintain consistent color palettes, mood, and charecters
5. Ensure that you use the gen_id of the first scene across all the images
"""
```

**Key Points**:
- Agent receives **ENTIRE screenplay** at once
- Agent has access to `generate_image` tool
- Agent decides how to process each scene
- Uses **gen_id** and **seed** for consistency

### Step 4: Gemini API Limitations

The notebook uses DALL-E 3 which supports:
- gen_id for character consistency
- seed for reproducibility

Gemini 2.5 Flash Image does NOT support these parameters directly. We need to:

**Option 1**: Simulate consistency with detailed prompts
- Include character description in EVERY prompt
- Use same color palette, lighting, style
- This is what we're currently trying

**Option 2**: Use DALL-E 3 instead
- Requires OpenAI API key
- Supports gen_id and seed natively
- Better consistency

**Option 3**: Use Imagen 3 (Google's image model)
- May have better consistency features
- Need to check API documentation

## Recommended Implementation Steps

### Phase 1: Quick Fix (Current Approach)
1. ✅ Use exact screenplay prompts (already done)
2. ✅ Parse scenes with structure (already done)
3. ⚠️ Improve prompt quality (partially done - using LLM agent)
4. ❌ Add retry logic with better error handling
5. ❌ Add delay between requests to avoid rate limiting

### Phase 2: Agent-Based Approach (Notebook Match)
1. ❌ Install LangGraph dependencies
2. ❌ Create StateGraph workflow
3. ❌ Implement storyboard agent with tool access
4. ❌ Pass entire screenplay to agent
5. ❌ Let agent decide how to process scenes
6. ❌ Implement consistency mechanism (gen_id equivalent)

### Phase 3: Alternative Image API
1. ❌ Evaluate DALL-E 3 vs Imagen 3
2. ❌ Implement gen_id/seed support
3. ❌ Test character consistency

## Current Status

✅ **Done**:
- Exact screenplay prompts from notebook
- Scene parsing with structure
- LLM agent for prompt enhancement

⚠️ **Partially Done**:
- Prompt quality (using LLM but not agent-based)
- Error handling (basic retry but not robust)

❌ **Not Done**:
- LangGraph architecture
- Agent-based storyboard generation
- gen_id/seed consistency mechanism
- Robust retry logic
- Rate limiting handling

## Next Steps

**Immediate** (to fix current issues):
1. Add exponential backoff retry logic
2. Add 2-3 second delay between image requests
3. Better error logging to see why Gemini blocks
4. Test with simpler prompts first, then gradually increase detail

**Long-term** (to match notebook):
1. Implement LangGraph workflow
2. Create agent-based storyboard generation
3. Evaluate alternative image APIs with consistency support
