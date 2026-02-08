# Complete LangGraph Prompts from 05_movie_storyboarding.ipynb

This document contains ALL the exact prompts used in the LangGraph notebook for reference and implementation.

---

## 1. CONCEPT CREATION PROMPT

```python
concept_creator_prompt = """You are an intelligent advertisement concept creator for any given theme.
Your job is to generate a concept for the given theme and justify it.
Note: You can search over internet for the references but make sure the concept is fresh and novel."""
```

**Usage**: 
- Input: Theme (user-provided brief/idea)
- Output: Creative concept with justification
- Tool: Web search (Tavily)

---

## 2. SCREENPLAY CREATION PROMPT - RAJAMOULI STYLE

```python
screenplay_writer_prompt = f"""#Context: You are an autonomous AI screenplay creation agent designed to create a screenplay for any given advertisement concept.

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

4. Scene Breakdown:

  a. Opening Scene:

    - Visuals: Describe the setting, atmosphere, and key visual elements.
    - Action: Detail the actions and movements of characters within the scene.
    - Camera Transition: Specify camera angles, movements, and transitions.
    - Close-Up: Highlight any close-up shots that emphasize emotions or significant details.
    - Text on Screen: Include any text that appears on screen, such as titles, captions, or subtitles.

  b. Middle Scenes:
    - Follow the same structure as the opening scene for each subsequent scene, ensuring continuity and coherence in the narrative.

  c. Climactic Scene:
    - Build up to the climax with heightened tension, dramatic reveals, and intense action.

  d. Ending Scene:
    - Resolve the main conflict, wrap up loose ends, and provide a satisfying conclusion.

Additional Notes:

  - STRICTLY RESTRICT THE SCREENPLAY WITH IN 3500 Characters.
  - Ensure the screenplay is engaging, emotionally resonant, and leaves a lasting impact on the audience.
  - Maintain the color palette, mood, and character consistency throughout the screenplay.
  - Incorporate Rajamouli's signature elements such as heroic feats, moral dilemmas, and visually stunning sequences.
  - Ensure the screenplay is engaging, emotionally resonant, and leaves a lasting impact on the audience.

Given Theme: {state['theme']}
Given Concept: {state['concept']}"""
```

**Usage**:
- Input: Theme + Concept
- Output: Screenplay in Rajamouli style (epic, grand scale)
- Tool: Web search (Tavily)

---

## 3. SCREENPLAY CREATION PROMPT - SHANKAR STYLE

```python
screenplay_writer_prompt = f"""#Context: You are an autonomous AI screenplay creation agent designed to create a screenplay for any given advertisement concept.

#Objective: Generate a unique, fresh, and novel screenplay for an advertisement concept.

#Guidelines:

1. Style and Inspiration:

  - The screenplay should be influenced by the style of Shankar, a renowned Indian cinema director known for his grandiose visuals, intricate storytelling, and socially relevant themes.
  -  The screenplay should reflect Shankar's cinematic experience, including high-impact visuals, compelling narratives, and dramatic sequences. Emphasize strong character development, elaborate sets, and emotional depth.

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

4. Scene Breakdown:

  a. Opening Scene:

    - Visuals: Describe the setting, atmosphere, and key visual elements.
    - Action: Detail the actions and movements of characters within the scene.
    - Camera Transition: Specify camera angles, movements, and transitions.
    - Close-Up: Highlight any close-up shots that emphasize emotions or significant details.
    - Text on Screen: Include any text that appears on screen, such as titles, captions, or subtitles.

  b. Middle Scenes:
    - Follow the same structure as the opening scene for each subsequent scene, ensuring continuity and coherence in the narrative.

  c. Climactic Scene:
    - Build up to the climax with heightened tension, dramatic reveals, and intense action.

  d. Ending Scene:
    - Resolve the main conflict, wrap up loose ends, and provide a satisfying conclusion.

Additional Notes:

  - STRICTLY RESTRICT THE SCREENPLAY WITH IN 3500 Characters.
  - Ensure the screenplay is engaging, emotionally resonant, and leaves a lasting impact on the audience.
  - Maintain the color palette, mood, and character consistency throughout the screenplay.
  - Incorporate Shankar's signature elements such as grandiose visuals, intricate storytelling, and socially relevant themes.
  - Ensure the screenplay is engaging, emotionally resonant, and leaves a lasting impact on the audience.

Given Theme: {state['theme']}
Given Concept: {state['concept']}"""
```

**Usage**:
- Input: Theme + Concept
- Output: Screenplay in Shankar style (high-tech, futuristic, social message)
- Tool: Web search (Tavily)

---

## 4. STORYBOARD IMAGE GENERATION PROMPT

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

**Usage**:
- Input: Complete screenplay with all scenes
- Output: Storyboard images for each scene
- Tool: DALL-E 3 image generation (in notebook) / Gemini 2.5 Flash Image (in our backend)
- **CRITICAL**: This agent processes the ENTIRE screenplay at once and generates images for ALL scenes iteratively

---

## KEY DIFFERENCES BETWEEN NOTEBOOK AND CURRENT IMPLEMENTATION

### 1. **Storyboard Generation Approach**

**Notebook**:
- Passes the ENTIRE screenplay to the storyboard agent
- Agent processes ALL scenes in one go
- Uses gen_id and seed for consistency across images
- Agent extracts scene information itself

**Current Backend**:
- Processes scenes ONE AT A TIME
- No gen_id or seed for consistency
- Manual scene extraction before image generation

### 2. **Scene Information**

**Notebook**:
- Screenplay includes: Visual, Sound, Camera Transition, Action, Close-Up, Text on Screen
- Rich, detailed scene descriptions from screenplay
- Justification with Relatability, Emotional Appeal, Visual Aesthetics, Clear Message

**Current Backend**:
- Only has: sceneNumber, duration, description
- Description is parsed from screenplay text
- Missing structured scene elements

### 3. **Image Generation**

**Notebook**:
- Uses DALL-E 3 with specific parameters
- gen_id for character consistency
- seed value for reproducibility
- Agent decides how to interpret each scene

**Current Backend**:
- Uses Gemini 2.5 Flash Image
- No consistency parameters
- Manual prompt construction per scene
- No agent decision-making

---

## RECOMMENDED FIXES

### Issue 1: "Generated outputs are irrelevant"

**Root Cause**: Scene parsing is losing the detailed structure from the screenplay. The notebook's screenplay includes structured fields (Visual, Sound, Camera, Action, Close-Up, Text) but our parsing only extracts generic "description".

**Solution**: 
1. Update screenplay prompts to explicitly format scenes with these fields
2. Update scene parsing to extract each field separately
3. Store structured scene data in the database

### Issue 2: "In description I can only see additional scene content"

**Root Cause**: The `parse_scenes()` function is concatenating all text and losing the structure. It's also skipping label lines like "Visual:", "Dialogue:", "Camera:".

**Solution**:
1. Parse scenes to preserve structure
2. Store Visual, Action, Camera, Close-Up, Text separately
3. Pass complete scene structure to image generation

### Issue 3: "Every time I couldn't see all images"

**Root Cause**: 
1. Gemini API may be rate-limiting or failing for some scenes
2. No retry logic
3. Processing scenes sequentially without proper error handling

**Solution**:
1. Add retry logic with exponential backoff
2. Better error handling and logging
3. Consider batch processing or parallel requests
4. Add fallback to continue even if one image fails

---

## CRITICAL INSIGHT

The notebook uses an **AGENT-BASED APPROACH** for storyboard generation:
- The storyboard agent receives the ENTIRE screenplay
- It has the `generate_image` tool available
- It decides HOW to process each scene
- It maintains consistency across all images using gen_id and seed

Our current implementation uses a **PROCEDURAL APPROACH**:
- We manually loop through scenes
- We construct prompts for each scene
- No agent decision-making
- No consistency mechanism

**To match the notebook's quality, we need to either**:
1. Implement the agent-based approach with LangChain/LangGraph
2. OR significantly improve our procedural approach with better prompts and consistency mechanisms
