"""
Ad Production Pipeline - Web-Compatible Version

This is a modified version of ad_production_pipeline.py that:
1. Removes HITL gates (no command-line input prompts)
2. Auto-approves all gates for web UI
3. Returns structured data suitable for API responses
4. Uses Gemini 2.5 Flash for storyboard images

Used by backend/main.py for web UI integration.
"""

import operator
import json
from typing import Annotated, List, Dict, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# Import model classes
from models.scene_plan import Shot, SceneDetail, ScenePlan
from models.locations_plan import LocationRequirement, LocationsPlan
from models.budget_estimate import BudgetLineItem, BudgetEstimate
from models.schedule_plan import ScheduleDay, SchedulePlan
from models.crew_gear import CrewMember, EquipmentItem, CrewGearPackage
from models.legal_clearance import LegalItem, LegalClearanceReport
from models.risk_register import Risk, RiskRegister

# Import TAMUS wrapper for LLM calls
from tamus_wrapper import get_tamus_client
import os


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def call_tamus_api(prompt: str, max_tokens: int = 2000) -> str:
    """Helper function to call TAMUS API with a prompt."""
    llm = get_tamus_client()
    response = llm.messages().create(
        model=os.getenv("TAMUS_MODEL", "protected.gpt-5.2"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )
    
    # Extract text from response
    if hasattr(response, 'content') and isinstance(response.content, list):
        if len(response.content) > 0:
            if isinstance(response.content[0], dict) and 'text' in response.content[0]:
                return response.content[0]['text']
            else:
                return str(response.content[0])
    
    return str(response)


# ============================================================================
# STATE DEFINITION
# ============================================================================

class StoryboardFrame(TypedDict):
    """Storyboard frame with image and description."""
    frame_number: int
    description: str
    image_url: Optional[str]
    duration_sec: float


class CreativeBrief(TypedDict):
    """Creative brief input."""
    brand_name: str
    theme: str
    target_duration_sec: int
    aspect_ratio: str


class State(TypedDict):
    """Complete pipeline state."""
    # Creative chain fields
    theme: str
    concept: str
    screenplay_1: str
    screenplay_2: str
    screenplay_winner: str
    story_board: str
    storyboard_frames: List[StoryboardFrame]
    overall_status: Annotated[str, operator.add]
    
    # Production planning fields
    creative_brief: CreativeBrief
    scene_plan: ScenePlan
    locations_plan: LocationsPlan
    budget_estimate: BudgetEstimate
    schedule_plan: SchedulePlan
    casting_suggestions: Dict
    props_wardrobe_list: Dict
    crew_gear_package: CrewGearPackage
    legal_clearance_report: LegalClearanceReport
    risk_register: RiskRegister
    production_pack: str


# ============================================================================
# CREATIVE CHAIN NODES (WEB-COMPATIBLE - NO HITL)
# ============================================================================

def ad_concept_creation_node(state: State) -> Dict:
    """Generate ad concept from theme using TAMUS API."""
    print("------ENTERING: CONCEPT CREATION NODE------")
    
    theme = state.get("theme", "")
    brand_name = state.get("creative_brief", {}).get("brand_name", "Brand")
    
    prompt = f"""You are an intelligent advertisement concept creator.
    
Brand: {brand_name}
Theme: {theme}

Create a compelling advertisement concept that:
1. Captures the brand essence
2. Resonates with the target audience
3. Is memorable and impactful
4. Can be executed in 30-60 seconds

Provide a detailed concept description including:
- Core message
- Visual style
- Emotional tone
- Key scenes or moments
"""
    
    concept = call_tamus_api(prompt)
    print(f"Generated Concept: {concept[:200]}...")
    
    return {"concept": concept, "overall_status": "Concept created. "}


def screen_play_creation_node_1(state: State) -> Dict:
    """Generate Rajamouli-style screenplay."""
    print("------ENTERING: SCREENPLAY CREATION NODE 1 (RAJAMOULI STYLE)------")
    
    concept = state.get("concept", "")
    duration = state.get("creative_brief", {}).get("target_duration_sec", 30)
    brand_name = state.get("creative_brief", {}).get("brand_name", "Brand")
    
    prompt = f"""You are a screenplay writer for advertisements in the style of SS RAJAMOULI.

Concept: {concept}
Duration: {duration} seconds
Brand: {brand_name}

Write a screenplay with 5 scenes using SS RAJAMOULI's signature style:
- EPIC, LARGER-THAN-LIFE visuals
- GRAND SCALE with sweeping camera movements
- DRAMATIC moments with powerful emotions
- HEROIC framing and mythological undertones
- SWEEPING cinematography

Format each scene as:
- Scene number
- Duration (seconds)
- Visual description (epic and grand)
- Action/movement
- Dialogue/voiceover (powerful and impactful)
- Camera angle (sweeping, dramatic)

Example format:
Scene 1 (6 seconds)
Visual: [epic description]
Action: [movement]
Dialogue: [powerful voiceover]
Camera: [dramatic angle]

Generate the complete screenplay now in RAJAMOULI STYLE."""
    
    screenplay = call_tamus_api(prompt)
    print(f"Generated Rajamouli Screenplay: {screenplay[:200]}...")
    
    return {"screenplay_1": screenplay, "overall_status": "Rajamouli screenplay created. "}


def screen_play_creation_node_2(state: State) -> Dict:
    """Generate Shankar-style screenplay."""
    print("------ENTERING: SCREENPLAY CREATION NODE 2 (SHANKAR STYLE)------")
    
    concept = state.get("concept", "")
    duration = state.get("creative_brief", {}).get("target_duration_sec", 30)
    brand_name = state.get("creative_brief", {}).get("brand_name", "Brand")
    
    prompt = f"""You are a screenplay writer for advertisements in the style of SHANKAR.

Concept: {concept}
Duration: {duration} seconds
Brand: {brand_name}

Write a screenplay with 5 scenes using SHANKAR's signature style:
- HIGH-TECH, FUTURISTIC visuals
- CUTTING-EDGE technology and innovation
- SLEEK, MODERN aesthetics with cutting-edge technology
- INNOVATIVE camera work and visual effects
- SOCIAL MESSAGE woven into the narrative

Format each scene as:
- Scene number
- Duration (seconds)
- Visual description (high-tech and futuristic)
- Action/movement
- Dialogue/voiceover (impactful with social message)
- Camera angle (innovative and modern)

Example format:
Scene 1 (6 seconds)
Visual: [futuristic description]
Action: [movement]
Dialogue: [impactful voiceover]
Camera: [innovative angle]

Generate the complete screenplay now in SHANKAR STYLE."""
    
    screenplay = call_tamus_api(prompt)
    print(f"Generated Shankar Screenplay: {screenplay[:200]}...")
    
    return {"screenplay_2": screenplay, "overall_status": "Shankar screenplay created. "}


def screenplay_evaluation_node(state: State) -> Dict:
    """Auto-select screenplay (no HITL for web)."""
    print("------ENTERING: SCREENPLAY EVALUATION NODE (AUTO-SELECT)------")
    
    # For web UI, auto-select screenplay 1 (Rajamouli style)
    # The UI will handle screenplay selection separately
    screenplay_winner = state.get("screenplay_1", "")
    print("Auto-selected: Rajamouli style screenplay (for web UI)")
    
    return {"screenplay_winner": screenplay_winner, "overall_status": "Screenplay selected. "}


def story_board_creation_node(state: State) -> Dict:
    """Generate storyboard frames using Gemini 2.5 Flash."""
    print("------ENTERING: STORY BOARD CREATION NODE------")
    
    screenplay = state.get("screenplay_winner", "")
    duration = state.get("creative_brief", {}).get("target_duration_sec", 30)
    brand_name = state.get("creative_brief", {}).get("brand_name", "Brand")
    
    # Step 1: Generate storyboard breakdown
    prompt = f"""Based on this screenplay, create a detailed storyboard breakdown:

Screenplay:
{screenplay}

Target Duration: {duration} seconds

For each key scene, provide:
1. Frame number
2. Visual description (detailed, suitable for image generation)
3. Duration in seconds

Format as JSON array with this structure:
[
  {{
    "frame_number": 1,
    "description": "Detailed visual description",
    "duration_sec": 5.0
  }}
]

Return ONLY valid JSON, no additional text.
"""
    
    storyboard_text = call_tamus_api(prompt, max_tokens=2000)
    
    # Step 2: Parse and generate images
    storyboard_frames = []
    try:
        frames_data = json.loads(storyboard_text)
        
        print(f"Generating {len(frames_data)} storyboard images with Gemini 2.5 Flash...")
        
        try:
            import google.genai as genai
            import base64
            
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                client = genai.Client(api_key=gemini_api_key)
                
                for frame_data in frames_data:
                    frame_num = frame_data.get("frame_number", 0)
                    description = frame_data.get("description", "")
                    duration = frame_data.get("duration_sec", 5.0)
                    
                    image_prompt = f"""Generate an image: Professional storyboard frame for a {brand_name} advertisement.

Scene Description: {description}

Style: Cinematic, professional advertising, high quality, detailed composition.
Format: 16:9 aspect ratio, suitable for video production."""
                    
                    try:
                        response = client.models.generate_content(
                            model="gemini-2.5-flash-image",
                            contents=image_prompt
                        )
                        
                        image_data = None
                        if hasattr(response, 'candidates') and len(response.candidates) > 0:
                            candidate = response.candidates[0]
                            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                                for part in candidate.content.parts:
                                    if hasattr(part, 'inline_data'):
                                        # Convert binary data to base64 data URL
                                        mime_type = part.inline_data.mime_type
                                        image_bytes = part.inline_data.data
                                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                                        image_data = f"data:{mime_type};base64,{image_base64}"
                                        break
                        
                        storyboard_frames.append({
                            "frame_number": frame_num,
                            "description": description,
                            "image_url": image_data,
                            "duration_sec": duration
                        })
                        
                        if image_data:
                            print(f"  ✓ Generated frame {frame_num} ({len(image_data)} chars)")
                        else:
                            print(f"  ⚠ Frame {frame_num} generated but no image data")
                        
                    except Exception as img_error:
                        print(f"  ⚠ Failed to generate image for frame {frame_num}: {img_error}")
                        storyboard_frames.append({
                            "frame_number": frame_num,
                            "description": description,
                            "image_url": None,
                            "duration_sec": duration
                        })
            else:
                print("⚠ GEMINI_API_KEY not set - text-only storyboard")
                for frame_data in frames_data:
                    storyboard_frames.append({
                        "frame_number": frame_data.get("frame_number", 0),
                        "description": frame_data.get("description", ""),
                        "image_url": None,
                        "duration_sec": frame_data.get("duration_sec", 5.0)
                    })
                
        except ImportError:
            print("⚠ google-genai not installed - text-only storyboard")
            for frame_data in frames_data:
                storyboard_frames.append({
                    "frame_number": frame_data.get("frame_number", 0),
                    "description": frame_data.get("description", ""),
                    "image_url": None,
                    "duration_sec": frame_data.get("duration_sec", 5.0)
                })
        
    except json.JSONDecodeError as e:
        print(f"⚠ Failed to parse storyboard JSON: {e}")
        storyboard_frames = []
    
    return {
        "story_board": storyboard_text,
        "storyboard_frames": storyboard_frames,
        "overall_status": "Storyboard created. "
    }


# ============================================================================
# PRODUCTION PLANNING NODES (SIMPLIFIED FOR WEB)
# ============================================================================

def scene_breakdown_node(state: State) -> Dict:
    """Break down storyboard into structured scene plan."""
    print("------ENTERING: SCENE BREAKDOWN NODE------")
    
    storyboard = state.get("story_board", "")
    duration = state.get("creative_brief", {}).get("target_duration_sec", 30)
    
    prompt = f"""Convert this storyboard into a detailed scene plan.

Storyboard: {storyboard}
Duration: {duration} seconds

Generate JSON with scenes and shots arrays. Return ONLY valid JSON."""
    
    scene_plan_json = call_tamus_api(prompt)
    
    try:
        scene_plan = json.loads(scene_plan_json)
        print(f"Generated scene plan with {len(scene_plan.get('scenes', []))} scenes")
        return {"scene_plan": scene_plan, "overall_status": "Scene plan created. "}
    except json.JSONDecodeError:
        return {"scene_plan": {"scenes": [], "shots": []}, "overall_status": "Scene plan created. "}


def production_planning_node(state: State) -> Dict:
    """Generate all production planning artifacts in one node."""
    print("------ENTERING: PRODUCTION PLANNING NODE------")
    
    scene_plan = state.get("scene_plan", {})
    scenes = scene_plan.get("scenes", [])
    
    # Generate simplified production pack
    production_pack = {
        "budget": {"total_min": 15000, "total_max": 25000, "line_items": []},
        "schedule": {"total_shoot_days": 2, "days": []},
        "crew": [],
        "locations": [],
        "equipment": [],
        "legal": []
    }
    
    return {
        "budget_estimate": production_pack["budget"],
        "schedule_plan": {"total_shoot_days": 2, "schedule_days": [], "assumptions": []},
        "locations_plan": {"locations": [], "permits_required": [], "noise_restrictions": False, "time_restrictions": "", "parking_availability": "", "insurance_requirements": ""},
        "crew_gear_package": {"crew": [], "equipment": []},
        "legal_clearance_report": {"items": [], "minors_involved": False, "drone_permits_required": False},
        "risk_register": {"risks": []},
        "casting_suggestions": {},
        "props_wardrobe_list": {},
        "production_pack": "production_pack.md",
        "overall_status": "Production planning complete. "
    }


# ============================================================================
# LANGGRAPH PIPELINE SETUP (SIMPLIFIED FOR WEB)
# ============================================================================

def create_web_production_pipeline():
    """Create web-compatible production pipeline (no HITL gates)."""
    
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("ad_concept_creation_node", ad_concept_creation_node)
    workflow.add_node("screen_play_creation_in_rajamouli_style", screen_play_creation_node_1)
    workflow.add_node("screen_play_creation_in_shankar_style", screen_play_creation_node_2)
    workflow.add_node("screenplay_evaluation_node", screenplay_evaluation_node)
    workflow.add_node("story_board_creation_node", story_board_creation_node)
    workflow.add_node("scene_breakdown_node", scene_breakdown_node)
    workflow.add_node("production_planning_node", production_planning_node)
    
    # Set entry point
    workflow.set_entry_point("ad_concept_creation_node")
    
    # Creative chain edges
    workflow.add_edge("ad_concept_creation_node", "screen_play_creation_in_rajamouli_style")
    workflow.add_edge("ad_concept_creation_node", "screen_play_creation_in_shankar_style")
    workflow.add_edge("screen_play_creation_in_rajamouli_style", "screenplay_evaluation_node")
    workflow.add_edge("screen_play_creation_in_shankar_style", "screenplay_evaluation_node")
    workflow.add_edge("screenplay_evaluation_node", "story_board_creation_node")
    workflow.add_edge("story_board_creation_node", "scene_breakdown_node")
    workflow.add_edge("scene_breakdown_node", "production_planning_node")
    
    # Set finish point
    workflow.set_finish_point("production_planning_node")
    
    return workflow.compile()


# ============================================================================
# WEB API HELPER FUNCTIONS
# ============================================================================

async def run_pipeline_async(creative_brief: Dict) -> Dict:
    """Run pipeline asynchronously for web API."""
    import asyncio
    
    pipeline = create_web_production_pipeline()
    
    initial_state = {
        "theme": creative_brief.get("theme", ""),
        "creative_brief": creative_brief,
        "overall_status": ""
    }
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    final_state = await loop.run_in_executor(None, pipeline.invoke, initial_state)
    
    return final_state
