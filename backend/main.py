"""
FastAPI Backend for Virtual Ad Agency Workspace
Wraps existing Python pipelines (ad_video_pipeline.py, ad_production_pipeline.py)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, Response
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import asyncio
import json
import uuid
import sys
import os
import io
import zipfile
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

# Get the parent directory (project root)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(parent_dir, '.env')

# Load .env file
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"✓ Loaded environment variables from: {env_path}")
    print(f"  - GEMINI_API_KEY: {'✓ Set' if os.getenv('GEMINI_API_KEY') else '✗ Not set'}")
    print(f"  - USE_TAMUS_API: {os.getenv('USE_TAMUS_API', 'false')}")
    print(f"  - TAMUS_API_KEY: {'✓ Set' if os.getenv('TAMUS_API_KEY') else '✗ Not set'}")
else:
    print(f"⚠ Warning: .env file not found at {env_path}")

# Add parent directory to path to import existing pipelines
sys.path.insert(0, parent_dir)

# Import your existing pipelines
try:
    # Import TAMUS wrapper for text generation
    from tamus_wrapper import get_tamus_client
    
    # Import LangGraph workflow
    from ad_workflow import run_ad_workflow
    
    # Import output formatter for clean LLM output
    from output_formatter import (
        parse_concept,
        parse_screenplay,
        format_concept_for_display,
        format_screenplay_for_display
    )
    
    PIPELINES_AVAILABLE = True
    print("✓ Successfully imported TAMUS wrapper")
    print("✓ Successfully imported LangGraph workflow")
    print("✓ Successfully imported output formatter")
except ImportError as e:
    print(f"✗ Warning: Could not import dependencies: {e}")
    print("  Running in MOCK MODE - no real AI generation")
    PIPELINES_AVAILABLE = False
except Exception as e:
    print(f"✗ Warning: Error initializing dependencies: {e}")
    print("  Running in MOCK MODE - no real AI generation")
    PIPELINES_AVAILABLE = False

# ============================================================================
# FastAPI App Setup
# ============================================================================

app = FastAPI(
    title="Virtual Ad Agency API",
    description="AI-powered ad production pipeline API",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:2500", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Data Models
# ============================================================================

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    ARCHIVED = "archived"

class WorkflowStep(str, Enum):
    BRIEF = "brief"
    CONCEPT = "concept"
    SCREENPLAYS = "screenplays"
    SELECT = "select"
    STORYBOARD = "storyboard"
    PRODUCTION = "production"
    EXPORT = "export"

class BudgetBand(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PREMIUM = "premium"

class Brief(BaseModel):
    platform: str
    duration: int
    budget: float
    location: str
    constraints: List[str] = []
    creativeDirection: str
    brandMandatories: List[str] = []
    targetAudience: str

class CreateProjectRequest(BaseModel):
    name: str
    client: str
    tags: List[str] = []
    budgetBand: BudgetBand

class SubmitBriefRequest(BaseModel):
    brief: Brief

class SelectScreenplayRequest(BaseModel):
    screenplayId: str

# ============================================================================
# In-Memory Storage (Replace with database in production)
# ============================================================================

projects_db: Dict[str, Dict[str, Any]] = {}
jobs_db: Dict[str, Dict[str, Any]] = {}

# ============================================================================
# Helper Functions
# ============================================================================

def create_job(project_id: str, step: str) -> Dict[str, Any]:
    """Create a new generation job"""
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "project_id": project_id,
        "step": step,
        "status": "pending",
        "progress": 0,
        "started_at": datetime.now().isoformat(),
        "estimated_time": 60,  # seconds
        "estimated_cost": 0.50,  # dollars
    }
    jobs_db[job_id] = job
    return job

async def run_generation(job_id: str, project_id: str, step: str, params: Dict[str, Any]):
    """Run generation in background"""
    job = jobs_db[job_id]
    project = projects_db[project_id]
    
    # Quiet mode - reduce verbose logging
    QUIET_MODE = os.getenv("QUIET_MODE", "false").lower() == "true"
    
    # Check if LangGraph workflow should be used
    USE_LANGGRAPH = os.getenv("USE_LANGGRAPH", "false").lower() == "true"
    
    try:
        job["status"] = "running"
        job["progress"] = 10
        
        if not PIPELINES_AVAILABLE:
            # Mock generation for testing (fallback)
            await asyncio.sleep(2)
            job["progress"] = 100
            job["status"] = "completed"
            # ... keep existing mock data ...
            return
        
        # ====================================================================
        # LANGGRAPH WORKFLOW (INTEGRATED FROM NOTEBOOK)
        # ====================================================================
        
        if USE_LANGGRAPH and step in ["concept", "screenplays"]:
            if not QUIET_MODE:
                print(f"\n{'='*60}")
                print(f"Using LangGraph Workflow (from notebook)")
                print(f"Project: {project_id}")
                print(f"{'='*60}\n")
            
            # Import LangGraph workflow
            from ad_workflow import run_ad_workflow
            
            # Build theme from brief
            brief = params.get("brief", project.get("brief", {}))
            theme = f"""Platform: {brief.get('platform', 'YouTube')}
Duration: {brief.get('duration', 30)} seconds
Budget: ${brief.get('budget', 50000):,}
Location: {brief.get('location', 'Studio')}
Creative Direction: {brief.get('creativeDirection', '')}
Brand: {', '.join(brief.get('brandMandatories', []))}
Target Audience: {brief.get('targetAudience', '')}
Constraints: {', '.join(brief.get('constraints', []))}"""
            
            job["progress"] = 20
            
            # Run LangGraph workflow
            print("Running LangGraph workflow...")
            workflow_result = await run_ad_workflow(theme)
            
            job["progress"] = 60
            
            # Store concept (with formatting)
            raw_concept = workflow_result["concept"]
            
            # Parse and format the concept
            try:
                parsed_concept = parse_concept(raw_concept)
                formatted_concept = format_concept_for_display(parsed_concept)
                print(f"✓ Concept parsed and formatted successfully")
            except Exception as format_error:
                print(f"⚠ Concept formatting failed: {format_error}, using raw output")
                formatted_concept = raw_concept
            
            project["concept"] = {
                "id": str(uuid.uuid4()),
                "title": parsed_concept.title if 'parsed_concept' in locals() else raw_concept[:100],
                "description": formatted_concept,  # Use formatted version
                "rawDescription": raw_concept,  # Keep raw for reference
                "keyMessage": brief.get('creativeDirection', ''),
                "visualStyle": "AI Generated (LangGraph)",
                "generatedAt": datetime.now().isoformat(),
                "version": 1
            }
            
            print(f"✓ Concept generated: {len(raw_concept)} characters (formatted: {len(formatted_concept)} characters)")
            
            job["progress"] = 70
            
            # Parse scenes from screenplays using output formatter
            def parse_scenes_from_screenplay(text, variant_name):
                """Parse screenplay text into structured scenes using output formatter"""
                try:
                    # Use the output formatter to parse the screenplay
                    parsed_screenplay = parse_screenplay(text, variant_name)
                    
                    # Convert to frontend format
                    scenes = []
                    for scene in parsed_screenplay.scenes:
                        # Build comprehensive description from all fields
                        description_parts = []
                        if scene.visuals:
                            description_parts.append(f"Visuals: {scene.visuals}")
                        if scene.action:
                            description_parts.append(f"Action: {scene.action}")
                        if scene.camera:
                            description_parts.append(f"Camera: {scene.camera}")
                        if scene.dialogue:
                            description_parts.append(f"Dialogue: {scene.dialogue}")
                        if scene.text_on_screen:
                            description_parts.append(f"Text on Screen: {scene.text_on_screen}")
                        
                        full_description = " | ".join(description_parts) if description_parts else f"{variant_name} - Scene {scene.scene_number}"
                        
                        scenes.append({
                            "sceneNumber": scene.scene_number,
                            "duration": scene.duration,
                            "description": full_description
                        })
                    
                    print(f"  ✓ Parsed {len(scenes)} scenes using output formatter for {variant_name}")
                    return scenes
                    
                except Exception as parse_error:
                    print(f"  ⚠ Output formatter failed: {parse_error}, using fallback parser")
                    # Fallback to simple parsing
                    scenes = []
                    lines = text.split('\n')
                    current_scene = None
                    current_field = None
                    
                    for line in lines:
                        line_stripped = line.strip()
                        
                        # Check if this is a scene header
                        if line_stripped.startswith('SCENE') or line_stripped.startswith('Scene') or line_stripped.startswith('##'):
                            # Save previous scene if exists
                            if current_scene and current_scene.get("description"):
                                scenes.append(current_scene)
                            
                            # Start new scene
                            import re
                            match = re.search(r'(\d+).*?\((\d+)s?\)', line_stripped)
                            if match:
                                current_scene = {
                                    "sceneNumber": int(match.group(1)),
                                    "duration": int(match.group(2)),
                                    "description": ""
                                }
                            else:
                                current_scene = {
                                    "sceneNumber": len(scenes) + 1,
                                    "duration": 6,
                                    "description": ""
                                }
                            current_field = None
                            continue
                        
                        if not current_scene or not line_stripped:
                            continue
                        
                        # Add content to description
                        current_scene["description"] += line_stripped + " "
                    
                    # Add last scene
                    if current_scene and current_scene.get("description"):
                        scenes.append(current_scene)
                    
                    # Clean up descriptions
                    for scene in scenes:
                        scene["description"] = scene["description"].strip()
                    
                    # Ensure we have at least 6 scenes
                    while len(scenes) < 6:
                        scene_num = len(scenes) + 1
                        scenes.append({
                            "sceneNumber": scene_num,
                            "duration": 5,
                            "description": f"{variant_name} - Scene {scene_num}: Epic visual sequence."
                        })
                    
                    return scenes[:6]
            
            scenes_a = parse_scenes_from_screenplay(workflow_result["screenplay_1"], "Rajamouli Style")
            scenes_b = parse_scenes_from_screenplay(workflow_result["screenplay_2"], "Shankar Style")
            
            # Format screenplays for display
            try:
                formatted_screenplay_a = format_screenplay_for_display(parse_screenplay(workflow_result["screenplay_1"], "Rajamouli Style"))
                formatted_screenplay_b = format_screenplay_for_display(parse_screenplay(workflow_result["screenplay_2"], "Shankar Style"))
                print(f"✓ Screenplays formatted successfully")
            except Exception as format_error:
                print(f"⚠ Screenplay formatting failed: {format_error}, using raw output")
                formatted_screenplay_a = workflow_result["screenplay_1"]
                formatted_screenplay_b = workflow_result["screenplay_2"]
            
            project["screenplays"] = [
                {
                    "id": str(uuid.uuid4()),
                    "variant": "A (Rajamouli Style)",
                    "scenes": scenes_a,
                    "totalDuration": sum(s.get("duration", 6) for s in scenes_a),
                    "scores": {"clarity": 8.5, "feasibility": 7.5, "costRisk": 6.5},
                    "generatedAt": datetime.now().isoformat(),
                    "formattedText": formatted_screenplay_a,  # Formatted version
                    "rawText": workflow_result["screenplay_1"]  # Raw version
                },
                {
                    "id": str(uuid.uuid4()),
                    "variant": "B (Shankar Style)",
                    "scenes": scenes_b,
                    "totalDuration": sum(s.get("duration", 6) for s in scenes_b),
                    "scores": {"clarity": 7.8, "feasibility": 8.2, "costRisk": 7.0},
                    "generatedAt": datetime.now().isoformat(),
                    "formattedText": formatted_screenplay_b,  # Formatted version
                    "rawText": workflow_result["screenplay_2"]  # Raw version
                }
            ]
            
            print(f"✓ Screenplays generated: Rajamouli ({len(scenes_a)} scenes), Shankar ({len(scenes_b)} scenes)")
            
            job["progress"] = 100
            job["status"] = "completed"
            job["completed_at"] = datetime.now().isoformat()
            
            print(f"\n{'='*60}")
            print(f"✓ LangGraph workflow completed")
            print(f"{'='*60}\n")
            
            return
        
        # ====================================================================
        # REAL PIPELINE EXECUTION - SIMPLIFIED (NO VIDEO GENERATION)
        # ====================================================================
        
        if not QUIET_MODE:
            print(f"\n{'='*60}")
            print(f"Starting REAL AI generation: {step}")
            print(f"Project: {project_id}")
            print(f"{'='*60}\n")
        
        if step == "concept":
            # ============================================================
            # STEP 1: Generate Concept (Text Only - No Video Pipeline)
            # ============================================================
            brief = params["brief"]
            
            job["progress"] = 30
            
            # Use TAMUS directly for concept generation (no video pipeline)
            from tamus_wrapper import get_tamus_client
            llm = get_tamus_client()
            
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

            print("Generating concept with TAMUS GPT-5.2..." if not QUIET_MODE else "")
            concept_response = await asyncio.to_thread(
                llm.messages().create,
                model=os.getenv("TAMUS_MODEL", "protected.gpt-5.2"),
                messages=[{"role": "user", "content": concept_prompt}],
                max_tokens=2000
            )
            
            # Extract text from response
            concept_text = ""
            if hasattr(concept_response, 'content'):
                content = concept_response.content
                if isinstance(content, list) and len(content) > 0:
                    # Response is a list of content blocks
                    if isinstance(content[0], dict) and 'text' in content[0]:
                        concept_text = content[0]['text']
                    else:
                        concept_text = str(content[0])
                elif isinstance(content, str):
                    concept_text = content
                else:
                    concept_text = str(content)
            else:
                concept_text = str(concept_response)
            
            print(f"✓ Concept generated: {len(concept_text)} characters")
            
            job["progress"] = 90
            
            # Parse and format the concept
            try:
                parsed_concept = parse_concept(concept_text)
                formatted_concept = format_concept_for_display(parsed_concept)
                print(f"✓ Concept parsed and formatted successfully")
            except Exception as format_error:
                print(f"⚠ Concept formatting failed: {format_error}, using raw output")
                formatted_concept = concept_text
                parsed_concept = None
            
            # Store concept
            project["concept"] = {
                "id": str(uuid.uuid4()),
                "title": parsed_concept.title if parsed_concept else concept_text[:100],
                "description": formatted_concept,  # Use formatted version
                "rawDescription": concept_text,  # Keep raw for reference
                "keyMessage": brief.get('creativeDirection', ''),
                "visualStyle": "AI Generated",
                "generatedAt": datetime.now().isoformat(),
                "version": 1
            }
            
            print(f"✓ Concept stored: {len(concept_text)} characters (formatted: {len(formatted_concept)} characters)")
            
        elif step == "screenplays":
            # ============================================================
            # STEP 2: Generate Screenplays (Text Only)
            # ============================================================
            job["progress"] = 30
            
            from tamus_wrapper import get_tamus_client
            llm = get_tamus_client()
            
            concept = project.get("concept", {}).get("description", "")
            brief = project.get("brief", {})
            
            # Generate Variant A - SS Rajamouli Style (Epic, Grand Scale)
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

4. Scene Breakdown (MUST HAVE EXACTLY 6 SCENES):

  a. Opening Scene:
    - Visuals: Describe the setting, atmosphere, and key visual elements in DETAIL.
    - Action: Detail the actions and movements of characters within the scene.
    - Camera Transition: Specify camera angles, movements, and transitions.
    - Close-Up: Highlight any close-up shots that emphasize emotions or significant details.
    - Text on Screen: Include any text that appears on screen, such as titles, captions, or subtitles.

  b. Middle Scenes (Scenes 2-5):
    - Follow the same structure as the opening scene for each subsequent scene, ensuring continuity and coherence in the narrative.

  c. Ending Scene (Scene 6):
    - Resolve the main conflict, wrap up loose ends, and provide a satisfying conclusion.

Additional Notes:
  - STRICTLY RESTRICT THE SCREENPLAY WITH IN 3500 Characters.
  - Ensure the screenplay is engaging, emotionally resonant, and leaves a lasting impact on the audience.
  - Maintain the color palette, mood, and character consistency throughout the screenplay.
  - Incorporate Rajamouli's signature elements such as heroic feats, moral dilemmas, and visually stunning sequences.
  - MUST HAVE EXACTLY 6 SCENES with detailed visual descriptions.

Given Concept: {concept}
Duration: {brief.get('duration', 30)} seconds
Platform: {brief.get('platform', 'YouTube')}

Generate the complete screenplay now in RAJAMOULI STYLE with EXACTLY 6 SCENES."""

            print("Generating screenplay variant A (SS Rajamouli style - Epic)...")
            screenplay_response_a = await asyncio.to_thread(
                llm.messages().create,
                model=os.getenv("TAMUS_MODEL", "protected.gpt-5.2"),
                messages=[{"role": "user", "content": screenplay_prompt_a}],
                max_tokens=2000
            )
            
            # Extract text from response A
            screenplay_text_a = ""
            if hasattr(screenplay_response_a, 'content'):
                content = screenplay_response_a.content
                if isinstance(content, list) and len(content) > 0:
                    if isinstance(content[0], dict) and 'text' in content[0]:
                        screenplay_text_a = content[0]['text']
                    else:
                        screenplay_text_a = str(content[0])
                elif isinstance(content, str):
                    screenplay_text_a = content
                else:
                    screenplay_text_a = str(content)
            else:
                screenplay_text_a = str(screenplay_response_a)
            
            job["progress"] = 50
            
            # Generate Variant B - Shankar Style (High-Tech, Futuristic)
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

4. Scene Breakdown (MUST HAVE EXACTLY 6 SCENES):

  a. Opening Scene:
    - Visuals: Describe the setting, atmosphere, and key visual elements in DETAIL.
    - Action: Detail the actions and movements of characters within the scene.
    - Camera Transition: Specify camera angles, movements, and transitions.
    - Close-Up: Highlight any close-up shots that emphasize emotions or significant details.
    - Text on Screen: Include any text that appears on screen, such as titles, captions, or subtitles.

  b. Middle Scenes (Scenes 2-5):
    - Follow the same structure as the opening scene for each subsequent scene, ensuring continuity and coherence in the narrative.

  c. Ending Scene (Scene 6):
    - Resolve the main conflict, wrap up loose ends, and provide a satisfying conclusion.

Additional Notes:
  - STRICTLY RESTRICT THE SCREENPLAY WITH IN 3500 Characters.
  - Ensure the screenplay is engaging, emotionally resonant, and leaves a lasting impact on the audience.
  - Maintain the color palette, mood, and character consistency throughout the screenplay.
  - Incorporate Shankar's signature elements such as grandiose visuals, intricate storytelling, and socially relevant themes.
  - MUST HAVE EXACTLY 6 SCENES with detailed visual descriptions.

Given Concept: {concept}
Duration: {brief.get('duration', 30)} seconds
Platform: {brief.get('platform', 'YouTube')}

Generate the complete screenplay now in SHANKAR STYLE with EXACTLY 6 SCENES."""

            print("Generating screenplay variant B (Shankar style - High-Tech)...")
            screenplay_response_b = await asyncio.to_thread(
                llm.messages().create,
                model=os.getenv("TAMUS_MODEL", "protected.gpt-5.2"),
                messages=[{"role": "user", "content": screenplay_prompt_b}],
                max_tokens=2000
            )
            
            # Extract text from response B
            screenplay_text_b = ""
            if hasattr(screenplay_response_b, 'content'):
                content = screenplay_response_b.content
                if isinstance(content, list) and len(content) > 0:
                    if isinstance(content[0], dict) and 'text' in content[0]:
                        screenplay_text_b = content[0]['text']
                    else:
                        screenplay_text_b = str(content[0])
                elif isinstance(content, str):
                    screenplay_text_b = content
                else:
                    screenplay_text_b = str(content)
            else:
                screenplay_text_b = str(screenplay_response_b)
            
            print(f"✓ Screenplay A (Rajamouli) generated: {len(screenplay_text_a)} characters")
            print(f"✓ Screenplay B (Shankar) generated: {len(screenplay_text_b)} characters")
            
            job["progress"] = 70
            
            # Parse scenes from screenplay using output formatter
            def parse_scenes_with_formatter(text, variant_name):
                """Parse screenplay text into structured scenes using output formatter"""
                print(f"\n[DEBUG] Parsing {variant_name}")
                print(f"[DEBUG] Screenplay text length: {len(text)} characters")
                print(f"[DEBUG] First 500 chars: {text[:500]}")
                
                try:
                    # Use the output formatter to parse the screenplay
                    parsed_screenplay = parse_screenplay(text, variant_name)
                    
                    # Convert to frontend format with all details
                    scenes = []
                    for scene in parsed_screenplay.scenes:
                        # Build comprehensive description from all fields
                        description_parts = []
                        if scene.visuals:
                            description_parts.append(scene.visuals)
                        if scene.action:
                            description_parts.append(scene.action)
                        
                        full_description = " ".join(description_parts) if description_parts else f"{variant_name} - Scene {scene.scene_number}"
                        
                        print(f"[DEBUG] Scene {scene.scene_number}: {full_description[:100]}...")
                        
                        scenes.append({
                            "sceneNumber": scene.scene_number,
                            "duration": scene.duration,
                            "description": full_description,
                            "visual": scene.visuals or "",
                            "action": scene.action or "",
                            "camera": scene.camera or "",
                            "dialogue": scene.dialogue or "",
                            "text_on_screen": scene.text_on_screen or ""
                        })
                    
                    print(f"  ✓ Parsed {len(scenes)} scenes using output formatter for {variant_name}")
                    return scenes[:6]  # Return first 6 scenes
                    
                except Exception as parse_error:
                    print(f"  ⚠ Output formatter failed: {parse_error}, using fallback parser")
                    # Fallback to original parsing logic
                    scenes = []
                    lines = text.split('\n')
                    current_scene = None
                    current_field = None
                    
                    for line in lines:
                        line_stripped = line.strip()
                        
                        # Check if this is a scene header
                        if line_stripped.startswith('SCENE') or line_stripped.startswith('Scene') or line_stripped.startswith('##'):
                            # Save previous scene if exists
                            if current_scene and current_scene.get("description"):
                                scenes.append(current_scene)
                            
                            # Start new scene
                            import re
                            match = re.search(r'(\d+).*?\((\d+)s?\)', line_stripped)
                            if match:
                                current_scene = {
                                    "sceneNumber": int(match.group(1)),
                                    "duration": int(match.group(2)),
                                    "description": "",
                                    "visual": "",
                                    "action": "",
                                    "camera": "",
                                    "dialogue": "",
                                    "text_on_screen": ""
                                }
                            else:
                                current_scene = {
                                    "sceneNumber": len(scenes) + 1,
                                    "duration": 6,
                                    "description": "",
                                    "visual": "",
                                    "action": "",
                                    "camera": "",
                                    "dialogue": "",
                                    "text_on_screen": ""
                                }
                            current_field = None
                            continue
                        
                        if not current_scene or not line_stripped:
                            continue
                        
                        # Check for field labels
                        if line_stripped.startswith('Visual:') or line_stripped.startswith('Visuals:'):
                            current_field = "visual"
                            content = line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else ""
                            if content:
                                current_scene["visual"] += content + " "
                                current_scene["description"] += content + " "
                        elif line_stripped.startswith('Action:'):
                            current_field = "action"
                            content = line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else ""
                            if content:
                                current_scene["action"] += content + " "
                                current_scene["description"] += content + " "
                        elif line_stripped.startswith('Camera:') or line_stripped.startswith('Camera Transition:'):
                            current_field = "camera"
                            content = line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else ""
                            if content:
                                current_scene["camera"] += content + " "
                        elif line_stripped.startswith('Dialogue:') or line_stripped.startswith('Dialog:'):
                            current_field = "dialogue"
                            content = line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else ""
                            if content:
                                current_scene["dialogue"] += content + " "
                        elif line_stripped.startswith('Close-Up:') or line_stripped.startswith('Close Up:'):
                            current_field = "visual"  # Add close-up to visual
                            content = line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else ""
                            if content:
                                current_scene["visual"] += "Close-up: " + content + " "
                                current_scene["description"] += "Close-up: " + content + " "
                        elif line_stripped.startswith('Text on Screen:') or line_stripped.startswith('Text:'):
                            current_field = "text_on_screen"
                            content = line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else ""
                            if content:
                                current_scene["text_on_screen"] += content + " "
                        elif current_field and line_stripped:
                            # Continue adding to current field
                            if current_field == "visual":
                                current_scene["visual"] += line_stripped + " "
                                current_scene["description"] += line_stripped + " "
                            elif current_field == "action":
                                current_scene["action"] += line_stripped + " "
                                current_scene["description"] += line_stripped + " "
                            elif current_field == "camera":
                                current_scene["camera"] += line_stripped + " "
                            elif current_field == "dialogue":
                                current_scene["dialogue"] += line_stripped + " "
                            elif current_field == "text_on_screen":
                                current_scene["text_on_screen"] += line_stripped + " "
                        elif line_stripped:
                            # No field label, add to description
                            current_scene["description"] += line_stripped + " "
                    
                    # Add last scene
                    if current_scene and current_scene.get("description"):
                        scenes.append(current_scene)
                    
                    # Clean up all fields
                    for scene in scenes:
                        scene["description"] = scene["description"].strip()
                        scene["visual"] = scene["visual"].strip()
                        scene["action"] = scene["action"].strip()
                        scene["camera"] = scene["camera"].strip()
                        scene["dialogue"] = scene["dialogue"].strip()
                        scene["text_on_screen"] = scene["text_on_screen"].strip()
                    
                    # Ensure we have at least 6 scenes with meaningful content
                    while len(scenes) < 6:
                        scene_num = len(scenes) + 1
                        scenes.append({
                            "sceneNumber": scene_num,
                            "duration": 5,
                            "description": f"{variant_name} - Scene {scene_num}: Epic visual sequence with dramatic action and emotional depth.",
                            "visual": f"Cinematic setting with {variant_name} style visuals",
                            "action": "Dynamic character movements and interactions",
                            "camera": "Sweeping camera movements with dramatic angles",
                            "dialogue": "",
                            "text_on_screen": ""
                        })
                    
                    # Validate descriptions
                    for scene in scenes:
                        if not scene["description"] or len(scene["description"]) < 20:
                            scene["description"] = f"{variant_name} - Scene {scene['sceneNumber']}: {scene.get('visual', 'Visual sequence')} {scene.get('action', 'with action')}"
                    
                    print(f"  Parsed {len(scenes)} scenes for {variant_name} (fallback)")
                    return scenes[:6]  # Return first 6 scenes
            
            scenes_a = parse_scenes_with_formatter(screenplay_text_a, "Rajamouli Style")
            scenes_b = parse_scenes_with_formatter(screenplay_text_b, "Shankar Style")
            
            # Format screenplays for display
            try:
                formatted_screenplay_a = format_screenplay_for_display(parse_screenplay(screenplay_text_a, "Rajamouli Style"))
                formatted_screenplay_b = format_screenplay_for_display(parse_screenplay(screenplay_text_b, "Shankar Style"))
                print(f"✓ Screenplays formatted successfully")
            except Exception as format_error:
                print(f"⚠ Screenplay formatting failed: {format_error}, using raw output")
                formatted_screenplay_a = screenplay_text_a
                formatted_screenplay_b = screenplay_text_b
            
            project["screenplays"] = [
                {
                    "id": str(uuid.uuid4()),
                    "variant": "A (Rajamouli Style)",
                    "scenes": scenes_a,
                    "totalDuration": sum(s.get("duration", 6) for s in scenes_a),
                    "scores": {"clarity": 8.5, "feasibility": 7.5, "costRisk": 6.5},
                    "generatedAt": datetime.now().isoformat(),
                    "formattedText": formatted_screenplay_a,  # Formatted version
                    "rawText": screenplay_text_a  # Raw version
                },
                {
                    "id": str(uuid.uuid4()),
                    "variant": "B (Shankar Style)",
                    "scenes": scenes_b,
                    "totalDuration": sum(s.get("duration", 6) for s in scenes_b),
                    "scores": {"clarity": 7.8, "feasibility": 8.2, "costRisk": 7.0},
                    "generatedAt": datetime.now().isoformat(),
                    "formattedText": formatted_screenplay_b,  # Formatted version
                    "rawText": screenplay_text_b  # Raw version
                }
            ]
            
            print(f"✓ Screenplays generated: Rajamouli ({len(scenes_a)} scenes), Shankar ({len(scenes_b)} scenes)")
            
        elif step == "storyboard":
            # ============================================================
            # STEP 3: Generate Storyboard
            # ============================================================
            
            if USE_LANGGRAPH:
                # Use LangGraph workflow for storyboard generation
                if not QUIET_MODE:
                    print(f"\n{'='*60}")
                    print(f"Using LangGraph Workflow for Storyboard")
                    print(f"{'='*60}\n")
                
                from ad_workflow import story_board_creation_node
                
                # Get selected screenplay
                screenplays = project.get("screenplays", [])
                selected_id = project.get("selectedScreenplay")
                selected_screenplay = next((s for s in screenplays if s["id"] == selected_id), screenplays[0] if screenplays else None)
                
                if not selected_screenplay:
                    raise ValueError("No screenplay selected")
                
                # Build screenplay text from scenes
                screenplay_text = f"Screenplay Variant: {selected_screenplay.get('variant', 'A')}\n\n"
                for scene in selected_screenplay.get("scenes", []):
                    screenplay_text += f"Scene {scene.get('sceneNumber', 1)} ({scene.get('duration', 6)}s):\n"
                    screenplay_text += f"{scene.get('description', '')}\n\n"
                
                # Prepare state for storyboard node
                state = {
                    "screenplay_winner": 1,
                    "screenplay_1": screenplay_text,
                    "screenplay_2": ""
                }
                
                job["progress"] = 20
                
                # Run storyboard creation node
                print("Running LangGraph storyboard creation node...")
                result = await story_board_creation_node(state)
                storyboard_text = result.get("story_board", "")
                
                job["progress"] = 50
                
                # Now generate images using Gemini
                scenes = selected_screenplay.get("scenes", [])
                
                try:
                    import google.genai as genai
                    import base64
                    
                    gemini_api_key = os.getenv("GEMINI_API_KEY")
                    if not gemini_api_key:
                        raise ValueError("GEMINI_API_KEY not set")
                    
                    gemini_client = genai.Client(api_key=gemini_api_key)
                    print("✓ Gemini client initialized")
                except Exception as e:
                    print(f"⚠ Warning: Could not initialize Gemini: {e}")
                    gemini_client = None
                
                # Parse the storyboard agent's output to extract detailed prompts
                # The agent should have generated detailed image descriptions
                print(f"Storyboard agent output length: {len(storyboard_text)} characters")
                print(f"First 500 chars: {storyboard_text[:500]}")
                
                # STEP 1: Extract character descriptions for consistency
                print("Extracting character descriptions for consistency...")
                character_prompt = f"""Analyze this screenplay and extract consistent character descriptions:

{selected_screenplay.get('rawText', '')[:3000]}

Extract:
1. Main character(s) physical appearance (age, gender, ethnicity, clothing, distinctive features)
2. Supporting characters (if any)
3. Visual style and tone

Return a concise character reference (2-3 sentences) that can be used to maintain consistency across all scenes.
Focus on visual details that an image generator needs."""

                try:
                    from tamus_wrapper import get_tamus_client
                    llm = get_tamus_client()
                    
                    character_response = await asyncio.to_thread(
                        llm.messages().create,
                        model=os.getenv("TAMUS_MODEL", "protected.gpt-5.2"),
                        messages=[{"role": "user", "content": character_prompt}],
                        max_tokens=500,
                        temperature=0.3  # Lower temperature for consistent character descriptions
                    )
                    
                    # Extract character description
                    character_description = ""
                    if hasattr(character_response, 'content'):
                        content = character_response.content
                        if isinstance(content, list) and len(content) > 0:
                            if isinstance(content[0], dict) and 'text' in content[0]:
                                character_description = content[0]['text']
                            else:
                                character_description = str(content[0])
                    
                    print(f"✓ Character description extracted: {character_description[:200]}...")
                except Exception as e:
                    print(f"⚠ Character extraction failed: {e}, proceeding without character reference")
                    character_description = ""
                
                storyboard_scenes = []
                total_scenes = len(scenes)
                
                for idx, scene in enumerate(scenes):
                    scene_number = scene.get("sceneNumber", idx + 1)
                    scene_description = scene.get("description", "")
                    scene_duration = scene.get("duration", 6)
                    
                    print(f"Processing scene {scene_number}/{total_scenes}...")
                    
                    # Generate image with Gemini
                    image_url = None
                    if gemini_client:
                        try:
                            # Build enhanced prompt with character consistency
                            consistency_note = ""
                            if character_description:
                                consistency_note = f"\n\nCHARACTER CONSISTENCY (maintain across all scenes):\n{character_description}"
                            
                            image_prompt = f"""Professional cinematic storyboard frame for advertisement.

Scene {scene_number} of {total_scenes}:
{scene_description}{consistency_note}

CRITICAL: Maintain exact same character appearance, clothing, and visual style as described above.
Style: Cinematic 16:9 format, professional advertising quality, photorealistic, high detail, dramatic lighting, premium aesthetics.
Temperature: 0.5 (for consistency)"""
                            
                            print(f"  Generating image for scene {scene_number}...")
                            print(f"  Prompt length: {len(image_prompt)} characters")
                            
                            # Use lower temperature for more consistent results
                            response = await asyncio.to_thread(
                                gemini_client.models.generate_content,
                                model="gemini-2.5-flash-image",
                                contents=image_prompt,
                                config={
                                    "temperature": 0.5,  # Lower temperature for consistency
                                    "top_p": 0.8,
                                    "top_k": 20
                                }
                            )
                            
                            # Extract image data - scan all parts for multiple formats
                            if hasattr(response, 'candidates') and len(response.candidates) > 0:
                                candidate = response.candidates[0]
                                
                                # Check finish reason
                                if hasattr(candidate, 'finish_reason'):
                                    finish_reason = str(candidate.finish_reason)
                                    print(f"  Finish reason: {finish_reason}")
                                    if 'SAFETY' in finish_reason or 'BLOCKED' in finish_reason:
                                        print(f"  ⚠ Content blocked by safety filters!")
                                
                                # Scan ALL parts for image data (not just parts[0])
                                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts') and len(candidate.content.parts) > 0:
                                    parts = candidate.content.parts
                                    print(f"  Response has {len(parts)} part(s)")
                                    
                                    # Try each part until we find image data
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
                                                # For now, log and continue to next part
                                                print(f"  ⚠ file_uri format not yet implemented, skipping")
                                        
                                        # Method 3: text part (no image)
                                        if hasattr(part, 'text') and part.text:
                                            print(f"  Part[{part_idx}] is text: {part.text[:100]}...")
                                    
                                    if not image_url:
                                        print(f"  ⚠ No image data found in any of {len(parts)} part(s)")
                                else:
                                    print(f"  ⚠ No content parts in candidate")
                            else:
                                print(f"  ⚠ No candidates in response")
                                
                        except Exception as img_error:
                            print(f"  ⚠ Image generation failed: {img_error}")
                            import traceback
                            traceback.print_exc()
                    
                    # FALLBACK: Use existing scene images if Gemini failed
                    if not image_url:
                        fallback_path = f"output/storyboard/scene_{scene_number}.png"
                        if os.path.exists(fallback_path):
                            print(f"  Using fallback image: {fallback_path}")
                            try:
                                with open(fallback_path, 'rb') as f:
                                    image_bytes = f.read()
                                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                                    image_url = f"data:image/png;base64,{image_base64}"
                                    print(f"  ✓ Fallback image loaded: {len(image_bytes)} bytes")
                            except Exception as e:
                                print(f"  ⚠ Failed to load fallback image: {e}")
                    
                    storyboard_scenes.append({
                        "id": str(uuid.uuid4()),
                        "sceneNumber": scene_number,
                        "duration": scene_duration,
                        "description": scene_description,
                        "dialogue": None,
                        "cameraAngle": "Medium shot",
                        "notes": "Generated with LangGraph workflow" if image_url and "fallback" not in str(image_url) else "Using fallback image from output folder",
                        "imageUrl": image_url
                    })
                    
                    progress = 50 + int((idx + 1) / total_scenes * 40)
                    job["progress"] = progress
                    
                    # Longer delay between requests to avoid rate limiting
                    if idx < len(scenes) - 1:
                        await asyncio.sleep(3)
                
                project["storyboard"] = {
                    "id": str(uuid.uuid4()),
                    "generatedAt": datetime.now().isoformat(),
                    "scenes": storyboard_scenes
                }
                
                images_generated = sum(1 for s in storyboard_scenes if s["imageUrl"])
                print(f"✓ Storyboard generated: {len(storyboard_scenes)} scenes ({images_generated} with images)")
                print(f"  Failed scenes: {[s['sceneNumber'] for s in storyboard_scenes if not s['imageUrl']]}")
                
            else:
                # Original storyboard generation (non-LangGraph)
                job["progress"] = 20
                
                # Get selected screenplay
                screenplays = project.get("screenplays", [])
                selected_id = project.get("selectedScreenplay")
                selected_screenplay = next((s for s in screenplays if s["id"] == selected_id), screenplays[0] if screenplays else None)
                
                if not selected_screenplay:
                    raise ValueError("No screenplay selected")
                
                scenes = selected_screenplay.get("scenes", [])
                print(f"Generating storyboard for {len(scenes)} scenes with LLM agent for character consistency...")
                
                # STEP 1: Use LLM to generate HIGH-QUALITY detailed prompts with character consistency
                from tamus_wrapper import get_tamus_client
                llm = get_tamus_client()
                
                # Build complete screenplay context
                screenplay_context = f"Screenplay Variant: {selected_screenplay.get('variant', 'A')}\n\n"
                for scene in scenes:
                    screenplay_context += f"Scene {scene.get('sceneNumber', 1)} ({scene.get('duration', 6)}s):\n"
                    screenplay_context += f"Description: {scene.get('description', '')}\n"
                    if scene.get('visual'):
                        screenplay_context += f"Visual: {scene.get('visual', '')}\n"
                    if scene.get('action'):
                        screenplay_context += f"Action: {scene.get('action', '')}\n"
                    if scene.get('camera'):
                        screenplay_context += f"Camera: {scene.get('camera', '')}\n"
                    if scene.get('dialogue'):
                        screenplay_context += f"Dialogue: {scene.get('dialogue', '')}\n"
                    screenplay_context += "\n"
                
                # Get brand from brief
                brief = project.get("brief", {})
                brand = ', '.join(brief.get('brandMandatories', ['Product']))
                
                # HIGH-QUALITY LLM Agent Prompt matching reference quality
                agent_prompt = f"""You are a professional storyboard artist creating detailed image generation prompts for a {brand} advertisement.

SCREENPLAY:
{screenplay_context}

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
  {{
    "scene_number": 1,
    "image_prompt": "Cinematic 16:9 storyboard frame... **Main character: [detailed description]**... [rest of detailed prompt]"
  }}
]

CRITICAL REQUIREMENTS:
- Use the EXACT SAME character description (in bold **like this**) in EVERY scene
- Include specific color palette (e.g., "deep teal, warm gold, charcoal")
- Describe camera movements (push-in, orbit, whip-pan, etc.)
- Add close-up emphasis on key details
- Include "Justification cues:" at the end
- Make prompts 300-500 words each for maximum quality
- Return ONLY valid JSON, no other text"""
                
                print("Using LLM agent to generate HIGH-QUALITY detailed prompts with character consistency...")
                
                agent_response = await asyncio.to_thread(
                    llm.messages().create,
                    model=os.getenv("TAMUS_MODEL", "protected.gpt-5.2"),
                    messages=[{"role": "user", "content": agent_prompt}],
                    max_tokens=6000  # Increased for detailed prompts
                )
                
                # Extract text from response
                agent_text = ""
                if hasattr(agent_response, 'content'):
                    content = agent_response.content
                    if isinstance(content, list) and len(content) > 0:
                        if isinstance(content[0], dict) and 'text' in content[0]:
                            agent_text = content[0]['text']
                        else:
                            agent_text = str(content[0])
                    elif isinstance(content, str):
                        agent_text = content
                    else:
                        agent_text = str(content)
                else:
                    agent_text = str(agent_response)
                
                # Parse JSON response
                try:
                    # Clean up response
                    agent_text = agent_text.strip()
                    if agent_text.startswith('```'):
                        lines = agent_text.split('\n')
                        agent_text = '\n'.join([line for line in lines if not line.startswith('```')])
                        agent_text = agent_text.strip()
                    
                    enhanced_prompts = json.loads(agent_text)
                    print(f"✓ LLM generated {len(enhanced_prompts)} HIGH-QUALITY detailed prompts with character consistency")
                except json.JSONDecodeError as e:
                    print(f"⚠ Failed to parse LLM response as JSON: {e}")
                    print(f"Response: {agent_text[:200]}...")
                    enhanced_prompts = []
                
                job["progress"] = 40
                
                # STEP 2: Generate images using Gemini with consistent prompts
                try:
                    import google.genai as genai
                    import base64
                    
                    gemini_api_key = os.getenv("GEMINI_API_KEY")
                    if not gemini_api_key:
                        raise ValueError("GEMINI_API_KEY not set")
                    
                    gemini_client = genai.Client(api_key=gemini_api_key)
                    print("✓ Gemini client initialized")
                except Exception as e:
                    print(f"⚠ Warning: Could not initialize Gemini: {e}")
                    print("  Generating storyboard without images")
                    gemini_client = None
                
                storyboard_scenes = []
                total_scenes = len(scenes)
                
                for idx, scene in enumerate(scenes):
                    scene_number = scene.get("sceneNumber", idx + 1)
                    scene_description = scene.get("description", "")
                    scene_duration = scene.get("duration", 6)
                    
                    print(f"Processing scene {scene_number}/{total_scenes}...")
                    
                    # Get enhanced prompt from LLM agent if available
                    enhanced_prompt = None
                    if enhanced_prompts:
                        for ep in enhanced_prompts:
                            if ep.get("scene_number") == scene_number:
                                enhanced_prompt = ep.get("image_prompt", "")
                                break
                    
                    # Generate image with Gemini if available
                    image_url = None
                    if gemini_client:
                        try:
                            # Use enhanced prompt from LLM agent, or fallback to basic prompt
                            if enhanced_prompt:
                                image_prompt = enhanced_prompt
                                print(f"  Using LLM-enhanced prompt ({len(image_prompt)} chars)")
                            else:
                                # Fallback prompt
                                image_prompt = f"""Generate a professional storyboard frame for an advertisement.

Scene {scene_number}: {scene_description}

Style: Cinematic, professional advertising quality, detailed composition, 16:9 aspect ratio, high quality, photorealistic."""
                            
                            print(f"  Generating image for scene {scene_number}...")
                            
                            # Generate image using Gemini 2.0 Flash Exp
                            response = await asyncio.to_thread(
                                gemini_client.models.generate_content,
                                model="gemini-2.5-flash-image",
                                contents=image_prompt
                            )
                            
                            # Extract image data with better error handling and retry logic
                            if (hasattr(response, 'candidates') and 
                                len(response.candidates) > 0):
                                
                                candidate = response.candidates[0]
                                
                                # Check for safety ratings (content blocked)
                                if hasattr(candidate, 'finish_reason'):
                                    finish_reason = str(candidate.finish_reason)
                                    if 'SAFETY' in finish_reason or 'BLOCKED' in finish_reason:
                                        print(f"  ⚠ Content blocked by safety filters: {finish_reason}")
                                
                                # Check if we have valid image data
                                has_image = False
                                if candidate and hasattr(candidate, 'content') and hasattr(candidate.content, 'parts') and len(candidate.content.parts) > 0:
                                    part = candidate.content.parts[0]
                                    if hasattr(part, 'inline_data') and part.inline_data is not None:
                                        if hasattr(part.inline_data, 'data') and part.inline_data.data is not None:
                                            has_image = True
                                            image_bytes = part.inline_data.data
                                            mime_type = part.inline_data.mime_type
                                            
                                            # Convert to base64 data URL
                                            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                                            image_url = f"data:{mime_type};base64,{image_base64}"
                                            
                                            print(f"  ✓ Image generated: {len(image_bytes)} bytes ({mime_type})")
                                
                                # If no image, try with ultra-simple prompt
                                if not has_image:
                                    print(f"  ⚠ No image data received, retrying with ultra-simple prompt...")
                                    # Extract just the key visual elements
                                    visual_desc = scene.get('visual', scene.get('description', ''))[:100]
                                    ultra_simple_prompt = f"Professional advertising photo: {visual_desc}. Clean, modern style. 16:9 format."
                                    
                                    try:
                                        response = await asyncio.to_thread(
                                            gemini_client.models.generate_content,
                                            model="gemini-2.5-flash-image",
                                            contents=ultra_simple_prompt
                                        )
                                        
                                        if hasattr(response, 'candidates') and len(response.candidates) > 0:
                                            candidate = response.candidates[0]
                                            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts') and len(candidate.content.parts) > 0:
                                                part = candidate.content.parts[0]
                                                if hasattr(part, 'inline_data') and part.inline_data is not None:
                                                    if hasattr(part.inline_data, 'data') and part.inline_data.data is not None:
                                                        image_bytes = part.inline_data.data
                                                        mime_type = part.inline_data.mime_type
                                                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                                                        image_url = f"data:{mime_type};base64,{image_base64}"
                                                        print(f"  ✓ Retry successful: {len(image_bytes)} bytes ({mime_type})")
                                                    else:
                                                        print(f"  ⚠ Retry failed: still no image data")
                                    except Exception as retry_error:
                                        print(f"  ⚠ Retry failed: {retry_error}")
                            else:
                                print(f"  ⚠ No candidates in response")
                                
                        except Exception as img_error:
                            print(f"  ⚠ Image generation failed for scene {scene_number}: {img_error}")
                            image_url = None
                    
                    # Create storyboard scene
                    storyboard_scenes.append({
                        "id": str(uuid.uuid4()),
                        "sceneNumber": scene_number,
                        "duration": scene_duration,
                        "description": scene_description,
                        "dialogue": scene.get("dialogue", None),
                        "cameraAngle": scene.get("camera", "Medium shot"),
                        "notes": "AI generated with LLM agent for character consistency" if enhanced_prompt else "AI generated storyboard",
                        "imageUrl": image_url
                    })
                    
                    # Update progress
                    progress = 40 + int((idx + 1) / total_scenes * 50)
                    job["progress"] = progress
                    
                    # Add delay between requests to avoid rate limiting (except for last scene)
                    if idx < len(scenes) - 1:
                        await asyncio.sleep(2)
                
                project["storyboard"] = {
                    "id": str(uuid.uuid4()),
                    "generatedAt": datetime.now().isoformat(),
                    "scenes": storyboard_scenes
                }
                
                images_generated = sum(1 for s in storyboard_scenes if s["imageUrl"])
                print(f"✓ Storyboard generated: {len(storyboard_scenes)} scenes ({images_generated} with images, character consistency: {len(enhanced_prompts) > 0})")
            
        elif step == "production":
            # ============================================================
            # STEP 4: Generate Production Pack (Using Production Pipeline)
            # ============================================================
            job["progress"] = 10
            
            # Import production pipeline functions
            from ad_production_pipeline import (
                scene_breakdown_node,
                location_planning_node,
                budgeting_node,
                schedule_ad_node,
                crew_gear_node,
                legal_clearance_node,
                risk_safety_node
            )
            
            # Get storyboard data
            storyboard = project.get("storyboard", {})
            scenes = storyboard.get("scenes", [])
            brief = project.get("brief", {})
            
            # Build storyboard text from scenes
            storyboard_text = ""
            for scene in scenes:
                storyboard_text += f"\n## Scene {scene.get('sceneNumber', 1)}\n"
                storyboard_text += f"Duration: {scene.get('duration', 5)}s\n"
                storyboard_text += f"Description: {scene.get('description', '')}\n"
                if scene.get('dialogue'):
                    storyboard_text += f"Dialogue: {scene.get('dialogue')}\n"
                if scene.get('cameraAngle'):
                    storyboard_text += f"Camera: {scene.get('cameraAngle')}\n"
            
            # Prepare state for production pipeline
            state = {
                "story_board": storyboard_text,
                "creative_brief": {
                    "brand_name": ', '.join(brief.get('brandMandatories', ['Brand'])),
                    "theme": brief.get('creativeDirection', ''),
                    "target_duration_sec": brief.get('duration', 30),
                    "aspect_ratio": "16:9"
                },
                "overall_status": ""
            }
            
            print(f"\n{'='*60}")
            print(f"Running Production Pipeline")
            print(f"Scenes: {len(scenes)}")
            print(f"{'='*60}\n")
            
            try:
                # Step 1: Scene Breakdown
                job["progress"] = 20
                print("1. Generating scene breakdown...")
                scene_result = await asyncio.to_thread(scene_breakdown_node, state)
                state.update(scene_result)
                
                if not state.get("scene_plan"):
                    raise ValueError("Scene breakdown failed")
                
                # Step 2: Run parallel planning nodes (with delays to avoid rate limiting)
                job["progress"] = 40
                print("2. Running planning nodes sequentially with delays...")
                
                # Location Planning
                print("   - Location planning...")
                location_result = await asyncio.to_thread(location_planning_node, state)
                state.update(location_result)
                await asyncio.sleep(3)  # 3 second delay between API calls
                
                # Budgeting
                job["progress"] = 50
                print("   - Budget estimation...")
                budget_result = await asyncio.to_thread(budgeting_node, state)
                state.update(budget_result)
                await asyncio.sleep(3)
                
                # Schedule
                job["progress"] = 60
                print("   - Schedule planning...")
                schedule_result = await asyncio.to_thread(schedule_ad_node, state)
                state.update(schedule_result)
                await asyncio.sleep(3)
                
                # Crew & Gear
                job["progress"] = 70
                print("   - Crew and gear planning...")
                crew_result = await asyncio.to_thread(crew_gear_node, state)
                state.update(crew_result)
                await asyncio.sleep(3)
                
                # Legal Clearances
                job["progress"] = 80
                print("   - Legal clearances...")
                legal_result = await asyncio.to_thread(legal_clearance_node, state)
                state.update(legal_result)
                await asyncio.sleep(3)
                
                # Risk Register
                job["progress"] = 85
                print("   - Risk assessment...")
                risk_result = await asyncio.to_thread(risk_safety_node, state)
                state.update(risk_result)
                
                # Step 3: Format production pack for frontend
                job["progress"] = 90
                print("3. Formatting production pack...")
                
                scene_plan = state.get("scene_plan", {})
                budget_estimate = state.get("budget_estimate", {})
                schedule_plan = state.get("schedule_plan", {})
                locations_plan = state.get("locations_plan", {})
                crew_gear = state.get("crew_gear", {})
                legal_clearances = state.get("legal_clearances", {})
                risk_register = state.get("risk_register", {})
                
                # Store production pack
                project["productionPack"] = {
                    "id": str(uuid.uuid4()),
                    "generatedAt": datetime.now().isoformat(),
                    "scenePlan": scene_plan,
                    "budget": {
                        "total_min": budget_estimate.get("total_min", 0),
                        "total_max": budget_estimate.get("total_max", 0),
                        "line_items": budget_estimate.get("line_items", []),
                        "assumptions": budget_estimate.get("assumptions", []),
                        "cost_drivers": budget_estimate.get("cost_drivers", [])
                    },
                    "schedule": {
                        "total_shoot_days": schedule_plan.get("total_shoot_days", 0),
                        "days": schedule_plan.get("days", []),
                        "company_moves": schedule_plan.get("company_moves", [])
                    },
                    "locations": locations_plan.get("locations", []),
                    "crew": crew_gear.get("crew", []),
                    "equipment": crew_gear.get("equipment", []),
                    "legal": legal_clearances.get("items", []),
                    "risks": risk_register.get("risks", [])
                }
                
                print(f"✓ Production pack generated successfully")
                print(f"  - Scenes: {len(scene_plan.get('scenes', []))}")
                print(f"  - Budget: ${budget_estimate.get('total_min', 0):,.0f} - ${budget_estimate.get('total_max', 0):,.0f}")
                print(f"  - Shoot days: {schedule_plan.get('total_shoot_days', 0)}")
                print(f"  - Locations: {len(locations_plan.get('locations', []))}")
                print(f"  - Crew: {len(crew_gear.get('crew', []))}")
                print(f"  - Risks: {len(risk_register.get('risks', []))}")
                
            except Exception as prod_error:
                print(f"⚠ Production pipeline error: {prod_error}")
                print("  Using partial results from production pipeline")
                import traceback
                traceback.print_exc()
                
                # Use whatever data we got, even if incomplete (NO DUMMY DATA)
                scene_plan = state.get("scene_plan", {})
                budget_estimate = state.get("budget_estimate", {})
                schedule_plan = state.get("schedule_plan", {})
                locations_plan = state.get("locations_plan", {})
                crew_gear = state.get("crew_gear", {})
                legal_clearances = state.get("legal_clearances", {})
                risk_register = state.get("risk_register", {})
                
                project["productionPack"] = {
                    "id": str(uuid.uuid4()),
                    "generatedAt": datetime.now().isoformat(),
                    "scenePlan": scene_plan,
                    "budget": {
                        "total_min": budget_estimate.get("total_min", 0),
                        "total_max": budget_estimate.get("total_max", 0),
                        "line_items": budget_estimate.get("line_items", []),
                        "assumptions": budget_estimate.get("assumptions", []),
                        "cost_drivers": budget_estimate.get("cost_drivers", [])
                    },
                    "schedule": {
                        "total_shoot_days": schedule_plan.get("total_shoot_days", 0),
                        "days": schedule_plan.get("days", []),
                        "company_moves": schedule_plan.get("company_moves", [])
                    },
                    "locations": locations_plan.get("locations", []),
                    "crew": crew_gear.get("crew", []),
                    "equipment": crew_gear.get("equipment", []),
                    "legal": legal_clearances.get("items", []),
                    "risks": risk_register.get("risks", []),
                    "error": str(prod_error)  # Include error for debugging
                }
                print(f"✓ Using partial production pack (some data may be incomplete)")
                print(f"  - Scenes: {len(scene_plan.get('scenes', []))}")
                print(f"  - Budget: ${budget_estimate.get('total_min', 0):,.0f} - ${budget_estimate.get('total_max', 0):,.0f}")
                print(f"  - Shoot days: {schedule_plan.get('total_shoot_days', 0)}")
                print(f"  - Locations: {len(locations_plan.get('locations', []))}")
                print(f"  - Crew: {len(crew_gear.get('crew', []))}")
                print(f"  - Risks: {len(risk_register.get('risks', []))}")
        
        job["progress"] = 100
        job["status"] = "completed"
        job["completed_at"] = datetime.now().isoformat()
        
        print(f"\n{'='*60}")
        print(f"✓ Generation completed: {step}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)
        print(f"\n✗ Generation failed: {e}")
        import traceback
        traceback.print_exc()
# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Virtual Ad Agency API",
        "pipelines_available": PIPELINES_AVAILABLE
    }

# Projects Endpoints
@app.get("/api/projects")
async def list_projects():
    """List all projects"""
    return list(projects_db.values())

@app.post("/api/projects")
async def create_project(request: CreateProjectRequest):
    """Create a new project"""
    project_id = str(uuid.uuid4())
    project = {
        "id": project_id,
        "name": request.name,
        "client": request.client,
        "status": ProjectStatus.DRAFT,
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "currentStep": WorkflowStep.BRIEF,
        "tags": request.tags,
        "budgetBand": request.budgetBand,
    }
    projects_db[project_id] = project
    return project

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get a single project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects_db[project_id]

@app.patch("/api/projects/{project_id}")
async def update_project(project_id: str, updates: Dict[str, Any]):
    """Update a project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    project.update(updates)
    project["updatedAt"] = datetime.now().isoformat()
    return project

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    del projects_db[project_id]
    return {"message": "Project deleted"}

# Brief Endpoints
@app.post("/api/projects/{project_id}/brief")
async def submit_brief(project_id: str, request: SubmitBriefRequest):
    """Submit a brief for a project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    project["brief"] = request.brief.model_dump()
    project["currentStep"] = WorkflowStep.CONCEPT
    project["updatedAt"] = datetime.now().isoformat()
    return project

# Generation Endpoints
@app.post("/api/projects/{project_id}/generate/concept")
async def generate_concept(project_id: str, background_tasks: BackgroundTasks):
    """Generate concept from brief"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if "brief" not in project:
        raise HTTPException(status_code=400, detail="Brief not submitted")
    
    job = create_job(project_id, "concept")
    background_tasks.add_task(
        run_generation,
        job["id"],
        project_id,
        "concept",
        {"brief": project["brief"]}
    )
    
    return {
        "jobId": job["id"],
        "estimatedTime": job["estimated_time"],
        "estimatedCost": job["estimated_cost"]
    }

@app.post("/api/projects/{project_id}/generate/screenplays")
async def generate_screenplays(project_id: str, background_tasks: BackgroundTasks):
    """Generate screenplay variants"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if "concept" not in project:
        raise HTTPException(status_code=400, detail="Concept not generated")
    
    job = create_job(project_id, "screenplays")
    background_tasks.add_task(
        run_generation,
        job["id"],
        project_id,
        "screenplays",
        {"conceptId": project["concept"]["id"]}
    )
    
    return {
        "jobId": job["id"],
        "estimatedTime": job["estimated_time"],
        "estimatedCost": job["estimated_cost"]
    }

@app.post("/api/projects/{project_id}/select/screenplay")
async def select_screenplay(project_id: str, request: SelectScreenplayRequest):
    """Select winning screenplay"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    project["selectedScreenplay"] = request.screenplayId
    project["currentStep"] = WorkflowStep.STORYBOARD
    project["updatedAt"] = datetime.now().isoformat()
    return project

@app.post("/api/projects/{project_id}/generate/storyboard")
async def generate_storyboard(project_id: str, background_tasks: BackgroundTasks):
    """Generate storyboard"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if "selectedScreenplay" not in project:
        raise HTTPException(status_code=400, detail="Screenplay not selected")
    
    job = create_job(project_id, "storyboard")
    background_tasks.add_task(
        run_generation,
        job["id"],
        project_id,
        "storyboard",
        {"screenplayId": project["selectedScreenplay"]}
    )
    
    return {
        "jobId": job["id"],
        "estimatedTime": job["estimated_time"],
        "estimatedCost": job["estimated_cost"]
    }

@app.post("/api/projects/{project_id}/generate/production")
async def generate_production_pack(project_id: str, background_tasks: BackgroundTasks):
    """Generate production pack"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    if "storyboard" not in project:
        raise HTTPException(status_code=400, detail="Storyboard not generated")
    
    job = create_job(project_id, "production")
    background_tasks.add_task(
        run_generation,
        job["id"],
        project_id,
        "production",
        {"storyboardId": project["storyboard"]["id"]}
    )
    
    return {
        "jobId": job["id"],
        "estimatedTime": job["estimated_time"],
        "estimatedCost": job["estimated_cost"]
    }

# Job Status Endpoint
@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs_db[job_id]

@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a job"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    job["status"] = "cancelled"
    return {"message": "Job cancelled"}

# SSE Endpoint for Progress Updates
@app.get("/api/stream/generation/{job_id}")
async def stream_generation_progress(job_id: str):
    """Stream generation progress via SSE"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    async def event_generator():
        job = jobs_db[job_id]
        
        while job["status"] in ["pending", "running"]:
            # Send progress update
            data = {
                "type": "progress",
                "data": {
                    "progress": job["progress"],
                    "step": job["step"],
                    "message": f"Processing {job['step']}..."
                }
            }
            yield f"data: {json.dumps(data)}\n\n"
            
            await asyncio.sleep(1)
        
        # Send completion or error
        if job["status"] == "completed":
            data = {
                "type": "complete",
                "data": {"message": "Generation completed"}
            }
        else:
            data = {
                "type": "error",
                "data": {"message": job.get("error", "Generation failed")}
            }
        
        yield f"data: {json.dumps(data)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

# ============================================================================
# Export Endpoints
# ============================================================================

@app.post("/api/projects/{project_id}/export")
async def export_project(project_id: str, formats: List[str]):
    """
    Export project in multiple formats (PDF, JSON, ZIP)
    
    Args:
        project_id: Project ID
        formats: List of format IDs ['pdf', 'json', 'docx', 'zip']
    
    Returns:
        Export job information
    """
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    return {
        "message": "Export prepared",
        "formats": formats,
        "projectId": project_id
    }

@app.get("/api/projects/{project_id}/export/json")
async def export_json(project_id: str):
    """Export project as JSON"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    # Create clean export data (include all available data, even if incomplete)
    export_data = {
        "project": {
            "id": project.get("id"),
            "name": project.get("name"),
            "client": project.get("client"),
            "status": project.get("status"),
            "exportedAt": datetime.now().isoformat()
        },
        "brief": project.get("brief", {}),
        "concept": project.get("concept", {}),
        "screenplays": project.get("screenplays", []),
        "selectedScreenplay": project.get("selectedScreenplay"),
        "storyboard": project.get("storyboard", {}),
        "productionPack": project.get("productionPack", {})
    }
    
    # Return as downloadable JSON
    json_str = json.dumps(export_data, indent=2)
    filename = f"{project.get('name', 'project').replace(' ', '_')}_export.json"
    
    return Response(
        content=json_str,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@app.get("/api/projects/{project_id}/export/markdown")
async def export_markdown(project_id: str):
    """Export project as Markdown production pack"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    brief = project.get("brief", {})
    concept = project.get("concept", {})
    storyboard = project.get("storyboard", {})
    production_pack = project.get("productionPack", {})
    
    # Build markdown content
    markdown = f"""# Production Pack: {project.get('name', 'Untitled Project')}

**Client:** {project.get('client', 'N/A')}
**Status:** {project.get('status', 'N/A')}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Table of Contents

1. [Project Brief](#project-brief)
2. [Creative Concept](#creative-concept)
3. [Storyboard](#storyboard)
4. [Budget Estimate](#budget-estimate)
5. [Schedule Plan](#schedule-plan)
6. [Locations](#locations)
7. [Crew & Equipment](#crew--equipment)
8. [Legal Clearances](#legal-clearances)
9. [Risk Register](#risk-register)

---

## Project Brief

**Platform:** {brief.get('platform', 'N/A')}
**Duration:** {brief.get('duration', 0)} seconds
**Budget:** ${brief.get('budget', 0):,}
**Location:** {brief.get('location', 'N/A')}

**Creative Direction:**
{brief.get('creativeDirection', 'N/A')}

**Target Audience:**
{brief.get('targetAudience', 'N/A')}

**Brand Mandatories:**
{', '.join(brief.get('brandMandatories', [])) if brief.get('brandMandatories') else 'N/A'}

**Constraints:**
{', '.join(brief.get('constraints', [])) if brief.get('constraints') else 'N/A'}

---

## Creative Concept

**Title:** {concept.get('title', 'N/A')}

**Description:**
{concept.get('description', 'N/A')}

**Key Message:**
{concept.get('keyMessage', 'N/A')}

**Visual Style:**
{concept.get('visualStyle', 'N/A')}

---

## Storyboard

"""
    
    # Add storyboard scenes
    scenes = storyboard.get("scenes", [])
    if scenes:
        for scene in scenes:
            markdown += f"""### Scene {scene.get('sceneNumber', 1)}

**Duration:** {scene.get('duration', 0)}s
**Camera:** {scene.get('cameraAngle', 'N/A')}

**Description:**
{scene.get('description', 'N/A')}

"""
            if scene.get('dialogue'):
                markdown += f"""**Dialogue:**
{scene.get('dialogue')}

"""
            if scene.get('notes'):
                markdown += f"""**Notes:**
{scene.get('notes')}

"""
    else:
        markdown += "*No storyboard scenes available*\n\n"
    
    markdown += """---

## Budget Estimate

"""
    
    # Add budget
    budget = production_pack.get("budget", {})
    if budget:
        markdown += f"""**Total Range:** ${budget.get('total_min', 0):,.2f} - ${budget.get('total_max', 0):,.2f}

### Line Items

"""
        
        for item in budget.get("line_items", []):
            markdown += f"""- **{item.get('category', 'N/A')} - {item.get('item', 'N/A')}**
  - Quantity: {item.get('quantity', 0)}
  - Unit Cost: ${item.get('unit_cost', 0):,.2f}
  - Total: ${item.get('total_cost', 0):,.2f}

"""
    else:
        markdown += "*Budget not yet generated*\n\n"
    
    markdown += """---

## Schedule Plan

"""
    
    # Add schedule
    schedule = production_pack.get("schedule", {})
    if schedule:
        markdown += f"""**Total Shoot Days:** {schedule.get('total_shoot_days', 0)}

"""
        
        for day in schedule.get("days", []):
            markdown += f"""### Day {day.get('day', 1)}

**Location:** {day.get('location', 'N/A')}
**Scenes:** {', '.join(map(str, day.get('scenes', [])))}

"""
    else:
        markdown += "*Schedule not yet generated*\n\n"
    
    markdown += """---

## Locations

"""
    
    # Add locations
    locations = production_pack.get("locations", [])
    if locations:
        for location in locations:
            markdown += f"""### {location.get('name', 'N/A')}

**Type:** {location.get('type', 'N/A')}
**Requirements:** {location.get('requirements', 'N/A')}

"""
    else:
        markdown += "*Locations not yet identified*\n\n"
    
    markdown += """---

## Crew & Equipment

### Crew

"""
    
    # Add crew
    crew = production_pack.get("crew", [])
    if crew:
        for crew_member in crew:
            markdown += f"""- **{crew_member.get('role', 'N/A')}**
  - {crew_member.get('responsibilities', 'N/A')}

"""
    else:
        markdown += "*Crew not yet assigned*\n\n"
    
    markdown += """### Equipment

"""
    
    # Add equipment
    equipment = production_pack.get("equipment", [])
    if equipment:
        for equip in equipment:
            markdown += f"""- {equip.get('item', 'N/A')} (Qty: {equip.get('quantity', 0)})

"""
    else:
        markdown += "*Equipment list not yet created*\n\n"
    
    markdown += """---

## Legal Clearances

"""
    
    # Add legal items
    legal_items = production_pack.get("legal", [])
    if legal_items:
        for item in legal_items:
            markdown += f"""- {item.get('item', 'N/A')}

"""
    else:
        markdown += "*No legal clearances identified*\n\n"
    
    markdown += """---

## Risk Register

"""
    
    # Add risks
    risks = production_pack.get("risks", [])
    if risks:
        for risk in risks:
            markdown += f"""### {risk.get('risk', 'N/A')}

**Severity:** {risk.get('severity', 'N/A')}
**Mitigation:** {risk.get('mitigation', 'N/A')}

"""
    else:
        markdown += "*No risks identified*\n\n"
    
    markdown += """---

*Generated by Virtual Ad Agency on """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "*\n"
    
    # Return as downloadable markdown
    filename = f"{project.get('name', 'project').replace(' ', '_')}_production_pack.md"
    
    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@app.get("/api/projects/{project_id}/export/zip")
async def export_zip(project_id: str):
    """Export project as ZIP archive with all files"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    # Create in-memory ZIP file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add JSON export
        export_data = {
            "project": {
                "id": project.get("id"),
                "name": project.get("name"),
                "client": project.get("client"),
                "exportedAt": datetime.now().isoformat()
            },
            "brief": project.get("brief", {}),
            "concept": project.get("concept", {}),
            "screenplays": project.get("screenplays", []),
            "selectedScreenplay": project.get("selectedScreenplay"),
            "storyboard": project.get("storyboard", {}),
            "productionPack": project.get("productionPack", {})
        }
        zip_file.writestr("project_data.json", json.dumps(export_data, indent=2))
        
        # Add markdown production pack
        # (Reuse markdown generation logic - simplified here)
        markdown_content = f"# {project.get('name', 'Project')}\n\nProduction pack exported on {datetime.now().isoformat()}"
        zip_file.writestr("production_pack.md", markdown_content)
        
        # Add README
        readme = f"""# {project.get('name', 'Project')} - Export Package

This package contains all project files exported from Virtual Ad Agency.

## Contents

- `project_data.json` - Complete project data in JSON format
- `production_pack.md` - Production pack in Markdown format

## Project Information

- **Client:** {project.get('client', 'N/A')}
- **Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

Generated by Virtual Ad Agency
"""
        zip_file.writestr("README.md", readme)
    
    # Prepare response
    zip_buffer.seek(0)
    filename = f"{project.get('name', 'project').replace(' ', '_')}_export.zip"
    
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=2501)
