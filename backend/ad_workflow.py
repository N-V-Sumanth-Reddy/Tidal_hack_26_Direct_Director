"""
LangGraph Workflow for Ad Production Pipeline
Exact implementation from 05_movie_storyboarding.ipynb
"""

import operator
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
import os
import base64
import asyncio

# Import TAMUS wrapper for text generation
from tamus_wrapper import get_tamus_client

# Import Gemini for image generation
import google.genai as genai

# Import LangChain components for Tavily search integration
from langchain_community.retrievers import TavilySearchAPIRetriever


# ============================================================================
# State Definition (from notebook)
# ============================================================================

class State(TypedDict):
    theme: str
    concept: str
    screenplay_1: str
    screenplay_2: str
    screenplay_winner: int
    story_board: str
    overall_status: Annotated[str, operator.add]


# ============================================================================
# Helper Functions for Tavily Search (simplified)
# ============================================================================

def search_web_for_context(query: str, max_results: int = 5) -> str:
    """
    Search the web using Tavily and return context for the LLM
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        Formatted search results as context string
    """
    try:
        retriever = TavilySearchAPIRetriever(k=max_results)
        results = retriever.invoke(query)
        
        if not results:
            return "No web search results found."
        
        # Format results as context
        context = "Web Search Results:\n\n"
        for idx, doc in enumerate(results, 1):
            context += f"{idx}. {doc.page_content}\n\n"
        
        return context
    except Exception as e:
        print(f"⚠ Tavily search failed: {e}")
        return "Web search unavailable."


# ============================================================================
# Node 1: Ad Concept Creation (with Tavily web search)
# ============================================================================

def ad_concept_creation_node(state):
    """
    Creates an advertisement concept from a theme using TAMUS GPT-5.2 with Tavily web search
    """
    print("------ENTERING: CONCEPT CREATION NODE------")
    
    # Search the web for inspiration and current trends
    print("  → Searching web for inspiration...")
    search_context = search_web_for_context(f"creative advertising concepts for {state['theme']}", max_results=3)
    
    concept_creator_prompt = f"""You are an intelligent advertisement concept creator for any given theme.
Your job is to generate a concept for the given theme and justify it.

{search_context}

Use the web search results above for inspiration, but make sure the concept is fresh and novel.

Theme: {state['theme']}

Generate a creative concept for this ad campaign."""
    
    # Use TAMUS for concept generation
    llm = get_tamus_client()
    
    response = llm.messages().create(
        model=os.getenv("TAMUS_MODEL", "protected.gpt-5.2"),
        messages=[{"role": "user", "content": concept_creator_prompt}],
        max_tokens=2000
    )
    
    # Extract text from response
    concept_text = ""
    if hasattr(response, 'content'):
        content = response.content
        if isinstance(content, list) and len(content) > 0:
            if isinstance(content[0], dict) and 'text' in content[0]:
                concept_text = content[0]['text']
            else:
                concept_text = str(content[0])
        elif isinstance(content, str):
            concept_text = content
        else:
            concept_text = str(content)
    else:
        concept_text = str(response)
    
    print(f"✓ Concept generated: {len(concept_text)} characters")
    
    return {"concept": concept_text}


# ============================================================================
# Node 2: Screenplay Creation - Rajamouli Style (with Tavily search)
# ============================================================================

def screen_play_creation_node_1(state):
    """
    Creates screenplay in SS Rajamouli style (epic, grand visuals) with Tavily web search
    """
    print("------ENTERING: SCREENPLAY CREATION NODE 1: In SS Rajamouli Style------")
    
    # Search the web for Rajamouli style references
    print("  → Searching web for Rajamouli style references...")
    search_context = search_web_for_context(f"SS Rajamouli filmmaking style epic storytelling", max_results=3)
    
    screenplay_writer_prompt = f"""#Context: You are an autonomous AI screenplay creation agent designed to create a screenplay for any given advertisement concept.

#Objective: Generate a unique, fresh, and novel screenplay for an advertisement concept.

#Guidelines:

1. Style and Inspiration:

  - The screenplay should be influenced by the style of SS Rajamouli, a renowned Indian cinema director known for his epic storytelling, grand visuals, and emotional depth.
  - Emulate the cinematic experience seen in Rajamouli's films, focusing on strong character development, dramatic plot twists, and visually captivating scenes.

{search_context}

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
    
    # Use TAMUS for screenplay generation
    llm = get_tamus_client()
    
    response = llm.messages().create(
        model=os.getenv("TAMUS_MODEL", "protected.gpt-5.2"),
        messages=[{"role": "user", "content": screenplay_writer_prompt}],
        max_tokens=2000
    )
    
    # Extract text from response
    screenplay_text = ""
    if hasattr(response, 'content'):
        content = response.content
        if isinstance(content, list) and len(content) > 0:
            if isinstance(content[0], dict) and 'text' in content[0]:
                screenplay_text = content[0]['text']
            else:
                screenplay_text = str(content[0])
        elif isinstance(content, str):
            screenplay_text = content
        else:
            screenplay_text = str(content)
    else:
        screenplay_text = str(response)
    
    print(f"✓ Screenplay 1 (Rajamouli) generated: {len(screenplay_text)} characters")
    
    return {"screenplay_1": screenplay_text}


# ============================================================================
# Node 3: Screenplay Creation - Shankar Style (with Tavily search)
# ============================================================================

def screen_play_creation_node_2(state):
    """
    Creates screenplay in Shankar style (high-tech, futuristic, social message) with Tavily web search
    """
    print("------ENTERING: SCREENPLAY CREATION NODE 2: In Shankar Style------")
    
    # Search the web for Shankar style references
    print("  → Searching web for Shankar style references...")
    search_context = search_web_for_context(f"Shankar director filmmaking style high-tech futuristic", max_results=3)
    
    screenplay_writer_prompt = f"""#Context: You are an autonomous AI screenplay creation agent designed to create a screenplay for any given advertisement concept.

#Objective: Generate a unique, fresh, and novel screenplay for an advertisement concept.

#Guidelines:

1. Style and Inspiration:

  - The screenplay should be influenced by the style of Shankar, a renowned Indian cinema director known for his grandiose visuals, intricate storytelling, and socially relevant themes.
  -  The screenplay should reflect Shankar's cinematic experience, including high-impact visuals, compelling narratives, and dramatic sequences. Emphasize strong character development, elaborate sets, and emotional depth.

{search_context}

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
    
    # Use TAMUS for screenplay generation
    llm = get_tamus_client()
    
    response = llm.messages().create(
        model=os.getenv("TAMUS_MODEL", "protected.gpt-5.2"),
        messages=[{"role": "user", "content": screenplay_writer_prompt}],
        max_tokens=2000
    )
    
    # Extract text from response
    screenplay_text = ""
    if hasattr(response, 'content'):
        content = response.content
        if isinstance(content, list) and len(content) > 0:
            if isinstance(content[0], dict) and 'text' in content[0]:
                screenplay_text = content[0]['text']
            else:
                screenplay_text = str(content[0])
        elif isinstance(content, str):
            screenplay_text = content
        else:
            screenplay_text = str(content)
    else:
        screenplay_text = str(response)
    
    print(f"✓ Screenplay 2 (Shankar) generated: {len(screenplay_text)} characters")
    
    return {"screenplay_2": screenplay_text}


# ============================================================================
# Node 4: Screenplay Evaluation (from notebook)
# ============================================================================

def screenplay_evaluation_node(state):
    """
    User selects which screenplay to use
    In the notebook, this is interactive. In our API, we'll default to screenplay_1
    """
    print("------ENTERING: SCREENPLAY EVALUATION NODE------")
    
    # For API usage, we'll default to screenplay_1 (Rajamouli style)
    # In a real implementation, this could be a user choice via API parameter
    screenplay_winner = "screenplay_1"
    
    print(f"✓ Selected screenplay: {screenplay_winner}")
    
    return {"screenplay_winner": 1}  # 1 for screenplay_1, 2 for screenplay_2


# ============================================================================
# Node 5: Storyboard Creation (from notebook - AGENT-BASED)
# ============================================================================

async def story_board_creation_node(state):
    """
    Creates storyboard images from the winning screenplay
    Exact implementation from notebook using agent-based approach
    """
    print("------ENTERING: STORY BOARD CREATION NODE------")
    
    # Get the winning screenplay
    screenplay_key = f"screenplay_{state['screenplay_winner']}"
    screenplay_text = state[screenplay_key]
    
    # Storyboard agent prompt (exact from notebook)
    story_board_prompt = """#Context: You are an autonomous AI image generation agent designed to create unique and high-quality images based on user-provided prompts. Your task is to interpret the given prompt creatively and generate an image that accurately reflects the described scene or concept.

#Objective: Generate images for storyboard creation for advertisements by adhering to the below guidelines

#Guidelines:

1. Receive and Process Multi-Scene Prompts:
    - The prompt will contain multiple scenes.
    - Each scene will include the following components: Visual, Sound, Camera Transition, Action, Close-Up, Text on Screen.
    - Also the prompt consists of Justification with Relatability, Emotional Appeal, Visual Aesthetics, Clear Message.

2. Iterative Scene Processing:
    - For each scene, extract the Visual, Sound, Camera Transition, Action, Close-Up, and Text on Screen elements.
    - Generate an image that accurately represents the combined essence of these elements.
    - Ensure consistency across all scenes by maintaining the same character descriptions, color palette, and visual style.

3. Image Generation Guidelines:
    - Visual: Focus on the main visual elements described. This includes the setting, objects, and characters.
    - Sound: Although sound is auditory, interpret and reflect the mood or atmosphere it conveys visually.
    - Camera Transition: Reflect the specified camera transitions (e.g., zoom, pan, tilt) to capture the dynamic aspect of the scene.
    - Action: Ensure the image captures the described action, emphasizing motion or interaction where applicable.
    - Close-Up: Highlight any specified close-up elements to focus on details or emotions.
    - Text on Screen: Integrate the provided text into the image, ensuring it complements the visual narrative.
    - Make sure you include the and follow Justification mentioned in Guidelines #1 in all the images that you generate

4. Consistency and Continuity:
    - Maintain consistent color palettes, mood, and characters across all scenes
    - Use the same character descriptions in every scene for consistency

Now, process the following screenplay and generate storyboard images for each scene:

{screenplay_text}"""
    
    # Use TAMUS to process the screenplay and generate image prompts
    llm = get_tamus_client()
    
    full_prompt = story_board_prompt.format(screenplay_text=screenplay_text)
    
    response = llm.messages().create(
        model=os.getenv("TAMUS_MODEL", "protected.gpt-5.2"),
        messages=[{"role": "user", "content": full_prompt}],
        max_tokens=6000
    )
    
    # Extract the agent's response
    agent_output = ""
    if hasattr(response, 'content'):
        content = response.content
        if isinstance(content, list) and len(content) > 0:
            if isinstance(content[0], dict) and 'text' in content[0]:
                agent_output = content[0]['text']
            else:
                agent_output = str(content[0])
        elif isinstance(content, str):
            agent_output = content
        else:
            agent_output = str(content)
    else:
        agent_output = str(response)
    
    print(f"✓ Storyboard agent processed screenplay: {len(agent_output)} characters")
    
    return {"story_board": agent_output}


# ============================================================================
# Build the LangGraph Workflow (exact from notebook)
# ============================================================================

def create_workflow():
    """
    Creates the LangGraph workflow exactly as in the notebook
    """
    workflow = StateGraph(State)
    
    # Add nodes (exact from notebook)
    workflow.add_node("ad_concept_creation_node", ad_concept_creation_node)
    workflow.add_node("screen_play_creation_in_rajamouli_style", screen_play_creation_node_1)
    workflow.add_node("screen_play_creation_in_shankar_style", screen_play_creation_node_2)
    workflow.add_node("screenplay_evaluation_node", screenplay_evaluation_node)
    workflow.add_node("story_board_creation_node", story_board_creation_node)
    
    # Set entry point (exact from notebook)
    workflow.set_entry_point("ad_concept_creation_node")
    
    # Add edges (exact from notebook)
    workflow.add_edge("ad_concept_creation_node", "screen_play_creation_in_rajamouli_style")
    workflow.add_edge("ad_concept_creation_node", "screen_play_creation_in_shankar_style")
    
    workflow.add_edge("screen_play_creation_in_rajamouli_style", "screenplay_evaluation_node")
    workflow.add_edge("screen_play_creation_in_shankar_style", "screenplay_evaluation_node")
    
    workflow.add_edge("screenplay_evaluation_node", "story_board_creation_node")
    
    # Set finish point (exact from notebook)
    workflow.set_finish_point("story_board_creation_node")
    
    # Compile the workflow
    app = workflow.compile()
    
    return app


# ============================================================================
# Main execution function for API integration
# ============================================================================

async def run_ad_workflow(theme: str):
    """
    Runs the complete ad workflow from theme to storyboard
    
    Args:
        theme: The advertisement theme/brief
        
    Returns:
        dict: Final state with concept, screenplays, and storyboard
    """
    print(f"\n{'='*60}")
    print(f"Starting Ad Workflow with LangGraph")
    print(f"Theme: {theme}")
    print(f"{'='*60}\n")
    
    # Create the workflow
    app = create_workflow()
    
    # Initial state
    initial_state = {
        "theme": theme,
        "concept": "",
        "screenplay_1": "",
        "screenplay_2": "",
        "screenplay_winner": 0,
        "story_board": "",
        "overall_status": ""
    }
    
    # Run the workflow
    final_state = await app.ainvoke(initial_state)
    
    print(f"\n{'='*60}")
    print(f"Ad Workflow Completed")
    print(f"{'='*60}\n")
    
    return final_state
