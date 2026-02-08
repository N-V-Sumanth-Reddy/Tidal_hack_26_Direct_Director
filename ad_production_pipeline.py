"""
Ad Production Multi-Agent Pipeline

This pipeline extends the creative chain (concept → screenplays → storyboard) with
comprehensive production planning nodes. It generates production-ready artifacts including:
- Scene breakdown with shots
- Location planning
- Budget estimation
- Schedule planning
- Crew and gear recommendations
- Legal clearances checklist
- Risk register
- Client review pack

The pipeline uses LangGraph for orchestration and includes HITL gates for human approval.
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
import re


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_json_from_llm_response(text: str) -> str:
    """
    Extract JSON from LLM response that may contain markdown code blocks or extra text.
    
    Args:
        text: Raw LLM response
        
    Returns:
        str: Extracted JSON string
    """
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'```', '', text)
    
    # Try to find JSON object or array
    # Look for outermost { } or [ ]
    json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if json_match:
        return json_match.group(1).strip()
    
    return text.strip()


def call_tamus_api(prompt: str, max_tokens: int = 4000, retries: int = 3) -> str:
    """
    Helper function to call TAMUS API with a prompt and retry logic.
    
    Args:
        prompt: The prompt to send to the LLM
        max_tokens: Maximum tokens in response
        retries: Number of retry attempts
        
    Returns:
        str: The LLM response text
        
    Raises:
        TimeoutError: If API times out after all retries
        ValueError: If response is empty after all retries
    """
    import time
    
    llm = get_tamus_client()
    
    # Log prompt length for debugging
    prompt_length = len(prompt)
    print(f"[TAMUS] Prompt length: {prompt_length} characters")
    
    # Warn if prompt is very long
    if prompt_length > 10000:
        print(f"  ⚠ Warning: Very long prompt ({prompt_length} chars)")
        print(f"  ⚠ This may cause API issues. Consider shortening the prompt.")
    
    # If prompt is extremely long, truncate it
    if prompt_length > 15000:
        print(f"  ⚠ Prompt too long ({prompt_length} chars), truncating to 15000 chars")
        prompt = prompt[:15000] + "\n\n[Prompt truncated due to length]"
    
    for attempt in range(retries):
        try:
            response = llm.messages().create(
                model=os.getenv("TAMUS_MODEL", "protected.gpt-5.2"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            
            # Extract text from response
            if hasattr(response, 'content') and isinstance(response.content, list):
                if len(response.content) > 0:
                    if isinstance(response.content[0], dict) and 'text' in response.content[0]:
                        text = response.content[0]['text']
                        if text and text.strip():
                            return text
                    else:
                        text = str(response.content[0])
                        if text and text.strip():
                            return text
            
            text = str(response)
            if text and text.strip():
                return text
                
            # If we got here, response was empty
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 3  # Increased backoff: 3s, 6s, 9s
                print(f"  ⚠ Empty response from TAMUS API, retrying in {wait_time}s... (attempt {attempt + 1}/{retries})")
                time.sleep(wait_time)
            else:
                raise ValueError("No content in response after all retries")
                
        except Exception as e:
            error_str = str(e).lower()
            is_timeout = 'timeout' in error_str or 'timed out' in error_str
            
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 3  # Increased backoff
                print(f"  ⚠ TAMUS API error: {e}, retrying in {wait_time}s... (attempt {attempt + 1}/{retries})")
                time.sleep(wait_time)
            else:
                print(f"  ✗ TAMUS API failed after {retries} attempts: {e}")
                # Raise TimeoutError specifically for timeout cases
                if is_timeout:
                    raise TimeoutError(f"TAMUS API timed out after {retries} attempts")
                raise
    
    raise ValueError("Failed to get response from TAMUS API")


def generate_synthetic_locations(scenes: List[Dict]) -> Dict:
    """Generate synthetic location data when API fails."""
    print("  → Generating synthetic location data...")
    
    # Extract unique locations from scenes
    unique_locations = {}
    for scene in scenes:
        loc_desc = scene.get('location_description', 'Studio')
        loc_type = scene.get('location_type', 'INT')
        if loc_desc not in unique_locations:
            unique_locations[loc_desc] = loc_type
    
    locations = []
    for idx, (loc_desc, loc_type) in enumerate(unique_locations.items(), 1):
        locations.append({
            "name": loc_desc,
            "type": loc_type,
            "description": f"Production location for {loc_desc}",
            "requirements": {
                "space": "Adequate space for crew and equipment",
                "power": "Standard power outlets required",
                "accessibility": "Accessible for crew and equipment"
            },
            "alternates": [
                f"Alternate {loc_desc} location A",
                f"Alternate {loc_desc} location B"
            ],
            "permits_required": loc_type == "EXT",
            "constraints": ["Weather dependent"] if loc_type == "EXT" else ["Noise control"]
        })
    
    return {
        "locations": locations,
        "total_locations": len(locations),
        "permits_needed": sum(1 for loc in locations if loc.get("permits_required", False)),
        "notes": "Synthetic data generated due to API timeout"
    }


def generate_synthetic_budget(scenes: List[Dict]) -> Dict:
    """Generate synthetic budget data when API fails."""
    print("  → Generating synthetic budget data...")
    
    num_scenes = len(scenes)
    base_cost = num_scenes * 5000  # $5k per scene baseline
    
    line_items = [
        {"category": "Crew", "description": "Director, DP, AD, Sound", "min": base_cost * 0.3, "max": base_cost * 0.4},
        {"category": "Equipment", "description": "Camera, lighting, grip, sound rental", "min": base_cost * 0.2, "max": base_cost * 0.3},
        {"category": "Location", "description": "Location fees and permits", "min": base_cost * 0.1, "max": base_cost * 0.15},
        {"category": "Talent", "description": "Cast and extras", "min": base_cost * 0.15, "max": base_cost * 0.2},
        {"category": "Post-Production", "description": "Editing, color, sound mix", "min": base_cost * 0.15, "max": base_cost * 0.2},
        {"category": "Insurance", "description": "Production insurance", "min": base_cost * 0.05, "max": base_cost * 0.05},
        {"category": "Contingency", "description": "Buffer for unexpected costs", "min": base_cost * 0.1, "max": base_cost * 0.125}
    ]
    
    total_min = sum(item["min"] for item in line_items)
    total_max = sum(item["max"] for item in line_items)
    
    return {
        "line_items": line_items,
        "total_min": total_min,
        "total_max": total_max,
        "assumptions": [
            f"Based on {num_scenes} scenes",
            "Standard crew rates",
            "Equipment rental for 2-3 days"
        ],
        "cost_drivers": [
            "Number of shooting days",
            "Location complexity",
            "Cast requirements"
        ],
        "notes": "Synthetic data generated due to API timeout"
    }


def generate_synthetic_schedule(scenes: List[Dict]) -> Dict:
    """Generate synthetic schedule data when API fails."""
    print("  → Generating synthetic schedule data...")
    
    num_scenes = len(scenes)
    shoot_days = max(2, (num_scenes + 2) // 3)  # ~3 scenes per day
    
    days = []
    for day_num in range(1, shoot_days + 1):
        start_idx = (day_num - 1) * 3
        end_idx = min(start_idx + 3, num_scenes)
        day_scenes = scenes[start_idx:end_idx]
        
        days.append({
            "day_number": day_num,
            "date": f"Day {day_num}",
            "scenes": [s.get("scene_number", idx + start_idx + 1) for idx, s in enumerate(day_scenes)],
            "location": day_scenes[0].get("location_description", "Studio") if day_scenes else "Studio",
            "call_time": "07:00",
            "wrap_time": "19:00",
            "notes": f"Shoot {len(day_scenes)} scenes"
        })
    
    return {
        "days": days,
        "total_days": shoot_days,
        "company_moves": max(1, shoot_days // 2),
        "prep_days": 2,
        "wrap_days": 1,
        "notes": "Synthetic data generated due to API timeout"
    }


def generate_synthetic_crew_gear(scenes: List[Dict]) -> Dict:
    """Generate synthetic crew and equipment data when API fails."""
    print("  → Generating synthetic crew/gear data...")
    
    crew = [
        {"role": "Director", "name": "TBD", "rate": 1500, "days": 5, "required": True},
        {"role": "Director of Photography", "name": "TBD", "rate": 1200, "days": 3, "required": True},
        {"role": "1st AD", "name": "TBD", "rate": 800, "days": 3, "required": True},
        {"role": "Sound Mixer", "name": "TBD", "rate": 600, "days": 3, "required": True},
        {"role": "Gaffer", "name": "TBD", "rate": 700, "days": 3, "required": True},
        {"role": "Key Grip", "name": "TBD", "rate": 650, "days": 3, "required": False}
    ]
    
    equipment = [
        {"item": "Camera Package", "description": "Cinema camera with lenses", "quantity": 1, "rate": 800, "days": 3, "required": True},
        {"item": "Lighting Package", "description": "LED and tungsten lights", "quantity": 1, "rate": 600, "days": 3, "required": True},
        {"item": "Grip Package", "description": "Stands, flags, diffusion", "quantity": 1, "rate": 400, "days": 3, "required": True},
        {"item": "Sound Package", "description": "Boom, lavs, recorder", "quantity": 1, "rate": 300, "days": 3, "required": True},
        {"item": "Monitors", "description": "On-set monitoring", "quantity": 2, "rate": 100, "days": 3, "required": False}
    ]
    
    return {
        "crew": crew,
        "equipment": equipment,
        "total_crew_cost": sum(c["rate"] * c["days"] for c in crew),
        "total_equipment_cost": sum(e["rate"] * e["days"] for e in equipment),
        "notes": "Synthetic data generated due to API timeout"
    }


def generate_synthetic_legal(scenes: List[Dict]) -> Dict:
    """Generate synthetic legal clearance data when API fails."""
    print("  → Generating synthetic legal data...")
    
    items = [
        {"item": "Location Releases", "status": "pending", "priority": "high", "notes": "Required for all locations"},
        {"item": "Talent Releases", "status": "pending", "priority": "high", "notes": "Required for all cast"},
        {"item": "Music Licensing", "status": "pending", "priority": "medium", "notes": "If using licensed music"},
        {"item": "Product Clearances", "status": "pending", "priority": "medium", "notes": "For visible brands/products"},
        {"item": "Insurance Certificate", "status": "pending", "priority": "high", "notes": "General liability required"}
    ]
    
    return {
        "items": items,
        "high_risk_count": sum(1 for item in items if item["priority"] == "high"),
        "pending_count": len(items),
        "notes": "Synthetic data generated due to API timeout"
    }


def generate_synthetic_risks(scenes: List[Dict]) -> Dict:
    """Generate synthetic risk register data when API fails."""
    print("  → Generating synthetic risk data...")
    
    risks = [
        {
            "risk": "Weather delays",
            "category": "schedule",
            "likelihood": "medium",
            "impact": "medium",
            "mitigation": "Have backup indoor locations, monitor weather forecasts"
        },
        {
            "risk": "Equipment failure",
            "category": "technical",
            "likelihood": "low",
            "impact": "high",
            "mitigation": "Have backup equipment, test all gear before shoot"
        },
        {
            "risk": "Talent unavailability",
            "category": "personnel",
            "likelihood": "low",
            "impact": "high",
            "mitigation": "Have backup talent, confirm schedules in advance"
        },
        {
            "risk": "Budget overrun",
            "category": "financial",
            "likelihood": "medium",
            "impact": "medium",
            "mitigation": "Track expenses daily, maintain contingency fund"
        }
    ]
    
    return {
        "risks": risks,
        "high_priority_count": sum(1 for r in risks if r["impact"] == "high"),
        "notes": "Synthetic data generated due to API timeout"
    }


# ============================================================================
# STATE DEFINITION
# ============================================================================

class StoryboardFrame(TypedDict):
    """Storyboard frame with image and description."""
    frame_number: int
    description: str
    image_url: str
    duration_sec: float


class CreativeBrief(TypedDict):
    """Creative brief input."""
    brand_name: str
    theme: str
    target_duration_sec: int
    aspect_ratio: str


class State(TypedDict):
    """Complete pipeline state."""
    # Creative chain fields (preserved from original pipeline)
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
    production_pack: str  # Path to final markdown/PDF


# ============================================================================
# CREATIVE CHAIN NODES (PRESERVED FROM ORIGINAL PIPELINE)
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
    """Manual human selection of winning screenplay (HITL gate)."""
    print("------ENTERING: SCREENPLAY EVALUATION NODE------")
    print("\n=== SCREENPLAY COMPARISON ===\n")
    
    print("VARIANT A (Rajamouli Style):")
    print(state.get("screenplay_1", "")[:500])
    print("\n" + "="*50 + "\n")
    
    print("VARIANT B (Shankar Style):")
    print(state.get("screenplay_2", "")[:500])
    print("\n" + "="*50 + "\n")
    
    user_input = input("Which screenplay did you like? Enter 1 (Rajamouli) or 2 (Shankar): ")
    
    if user_input == "1":
        screenplay_winner = state.get("screenplay_1", "")
        print("Selected: Rajamouli style screenplay")
    else:
        screenplay_winner = state.get("screenplay_2", "")
        print("Selected: Shankar style screenplay")
    
    return {"screenplay_winner": screenplay_winner, "overall_status": "Screenplay selected. "}


def story_board_creation_node(state: State) -> Dict:
    """Generate storyboard frames using Gemini 2.5 Flash."""
    print("------ENTERING: STORY BOARD CREATION NODE------")
    
    screenplay = state.get("screenplay_winner", "")
    duration = state.get("creative_brief", {}).get("target_duration_sec", 30)
    brand_name = state.get("creative_brief", {}).get("brand_name", "Brand")
    
    # Step 1: Generate storyboard breakdown (text descriptions)
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
    
    # Step 2: Parse storyboard JSON
    storyboard_frames = []
    try:
        frames_data = json.loads(storyboard_text)
        
        # Step 3: Generate images for each frame using Gemini 2.5 Flash
        print(f"Generating {len(frames_data)} storyboard images with Gemini 2.5 Flash...")
        
        try:
            import google.genai as genai
            
            # Initialize Gemini client
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                print("⚠ GEMINI_API_KEY not set - skipping image generation")
                # Return text-only storyboard
                for frame_data in frames_data:
                    storyboard_frames.append({
                        "frame_number": frame_data.get("frame_number", 0),
                        "description": frame_data.get("description", ""),
                        "image_url": None,  # No image generated
                        "duration_sec": frame_data.get("duration_sec", 5.0)
                    })
            else:
                client = genai.Client(api_key=gemini_api_key)
                
                for frame_data in frames_data:
                    frame_num = frame_data.get("frame_number", 0)
                    description = frame_data.get("description", "")
                    duration = frame_data.get("duration_sec", 5.0)
                    
                    # Generate image with Gemini 2.5 Flash
                    image_prompt = f"""Create a professional storyboard frame for a {brand_name} advertisement.

Scene Description: {description}

Style: Cinematic, professional advertising, high quality, detailed composition.
Format: 16:9 aspect ratio, suitable for video production."""
                    
                    try:
                        # Generate image using Gemini 2.5 Flash
                        response = client.models.generate_images(
                            model="gemini-2.5-flash",
                            prompt=image_prompt,
                            config={
                                "number_of_images": 1,
                                "aspect_ratio": "16:9"
                            }
                        )
                        
                        # Extract image URL from response
                        image_url = None
                        if hasattr(response, 'generated_images') and len(response.generated_images) > 0:
                            image_url = response.generated_images[0].image.url
                        
                        storyboard_frames.append({
                            "frame_number": frame_num,
                            "description": description,
                            "image_url": image_url,
                            "duration_sec": duration
                        })
                        
                        print(f"  ✓ Generated frame {frame_num}")
                        
                    except Exception as img_error:
                        print(f"  ⚠ Failed to generate image for frame {frame_num}: {img_error}")
                        # Add frame without image
                        storyboard_frames.append({
                            "frame_number": frame_num,
                            "description": description,
                            "image_url": None,
                            "duration_sec": duration
                        })
                
                print(f"✓ Generated {len(storyboard_frames)} storyboard frames")
                
        except ImportError:
            print("⚠ google-genai package not installed - skipping image generation")
            # Return text-only storyboard
            for frame_data in frames_data:
                storyboard_frames.append({
                    "frame_number": frame_data.get("frame_number", 0),
                    "description": frame_data.get("description", ""),
                    "image_url": None,
                    "duration_sec": frame_data.get("duration_sec", 5.0)
                })
        
    except json.JSONDecodeError as e:
        print(f"⚠ Failed to parse storyboard JSON: {e}")
        print(f"Response: {storyboard_text[:200]}...")
        # Return empty frames
        storyboard_frames = []
    
    return {
        "story_board": storyboard_text,
        "storyboard_frames": storyboard_frames,
        "overall_status": "Storyboard created. "
    }


# ============================================================================
# PRODUCTION PLANNING NODES
# ============================================================================

def scene_breakdown_node(state: State) -> Dict:
    """Break down storyboard into structured scene plan with shots."""
    print("------ENTERING: SCENE BREAKDOWN NODE------")
    
    storyboard = state.get("story_board", "")
    duration = state.get("creative_brief", {}).get("target_duration_sec", 30)
    brand_name = state.get("creative_brief", {}).get("brand_name", "Brand")
    
    prompt = f"""You are a production planning specialist. Convert the following storyboard into a detailed scene plan.

Storyboard:
{storyboard}

Brand: {brand_name}
Target Duration: {duration} seconds

Generate a scene plan in strict JSON format with:
- scenes: array of scene objects with scene_id, duration_sec, location_type (INT/EXT), time_of_day (DAY/NIGHT), 
  location_description, cast_count, props, wardrobe, sfx_vfx, dialogue_vo, on_screen_text
- shots: array of shot objects with shot_id, scene_id, shot_type (WIDE/MEDIUM/CLOSE-UP/INSERT/POV), 
  camera_movement (STATIC/PAN/TILT/DOLLY/STEADICAM), duration_sec, description

Requirements:
- Each scene must have 2-5 shots
- Sum of shot durations must equal scene duration (±1 second)
- Use standard shot types and camera movements
- Include all props, wardrobe, and effects visible in storyboard

Return ONLY valid JSON, no additional text.
"""
    
    # Increased max_tokens to 6000 to accommodate reasoning tokens + output
    scene_plan_json = call_tamus_api(prompt, max_tokens=6000)
    
    try:
        # Extract JSON from response (handles markdown code blocks)
        clean_json = extract_json_from_llm_response(scene_plan_json)
        scene_plan = json.loads(clean_json)
        print(f"✓ Generated scene plan with {len(scene_plan.get('scenes', []))} scenes")
        return {"scene_plan": scene_plan, "overall_status": "Scene plan created. "}
    except json.JSONDecodeError as e:
        print(f"⚠ Error parsing scene plan JSON: {e}")
        print(f"  Response preview: {scene_plan_json[:200]}...")
        # Return empty scene plan instead of failing
        return {
            "scene_plan": {"scenes": [], "shots": []},
            "overall_status": f"Scene plan parsing failed, using empty plan. "
        }


def scene_plan_approval_gate(state: State) -> Dict:
    """Display scene plan for human approval (HITL gate)."""
    print("------ENTERING: SCENE PLAN APPROVAL GATE------")
    
    scene_plan = state.get("scene_plan", {})
    scenes = scene_plan.get("scenes", [])
    shots = scene_plan.get("shots", [])
    
    print("\n=== SCENE PLAN SUMMARY ===")
    print(f"Total Scenes: {len(scenes)}")
    print(f"Total Shots: {len(shots)}")
    print(f"Total Duration: {sum(s.get('duration_sec', 0) for s in scenes):.1f} seconds")
    
    # Show scene breakdown
    for scene in scenes:
        print(f"\n{scene.get('scene_id')}: {scene.get('location_description')}")
        print(f"  Type: {scene.get('location_type')} - {scene.get('time_of_day')}")
        print(f"  Duration: {scene.get('duration_sec')}s")
        print(f"  Cast: {scene.get('cast_count')}")
        print(f"  Props: {', '.join(scene.get('props', []))}")
    
    approval = input("\nApprove scene plan? (yes/no): ").lower()
    
    if approval == "yes":
        return {"overall_status": "Scene plan approved. "}
    else:
        return {"overall_status": "Scene plan rejected. "}


def location_planning_node(state: State) -> Dict:
    """Generate location requirements and permit checklist."""
    print("------ENTERING: LOCATION PLANNING NODE------")
    
    scene_plan = state.get("scene_plan", {})
    scenes = scene_plan.get("scenes", [])
    
    # Extract unique locations
    locations_text = "\n".join([
        f"- {s.get('location_description', 'Unknown')} ({s.get('location_type', 'INT')} - {s.get('time_of_day', 'DAY')})"
        for s in scenes
    ])
    
    prompt = f"""You are a location scout. Generate location requirements for these scenes:

{locations_text}

For each unique location, provide:
1. Primary location requirements (type, description, key features)
2. Accessibility, power, and space requirements
3. 2-3 alternate location suggestions
4. Permit and constraint checklist

Return as JSON matching LocationsPlan schema with locations array and permit fields.
"""
    
    try:
        # Increased max_tokens to 8000 to accommodate reasoning tokens + output
        locations_json = call_tamus_api(prompt, max_tokens=8000)
        # Extract JSON from response
        clean_json = extract_json_from_llm_response(locations_json)
        locations_plan = json.loads(clean_json)
        print(f"✓ Generated locations plan with {len(locations_plan.get('locations', []))} locations")
        return {"locations_plan": locations_plan, "overall_status": "Locations plan created. "}
    except TimeoutError:
        print(f"⚠ API timeout - using synthetic location data")
        locations_plan = generate_synthetic_locations(scenes)
        return {"locations_plan": locations_plan, "overall_status": "Locations plan created (synthetic). "}
    except (json.JSONDecodeError, Exception) as e:
        print(f"⚠ Error: {e} - using synthetic location data")
        locations_plan = generate_synthetic_locations(scenes)
        return {"locations_plan": locations_plan, "overall_status": "Locations plan created (synthetic). "}


def budgeting_node(state: State) -> Dict:
    """Generate budget estimate with line items."""
    print("------ENTERING: BUDGETING NODE------")
    
    scene_plan = state.get("scene_plan", {})
    scenes = scene_plan.get("scenes", [])
    
    scene_summary = f"Total scenes: {len(scenes)}, Total cast: {sum(s.get('cast_count', 0) for s in scenes)}"
    
    prompt = f"""You are a production budget estimator. Generate a detailed budget for this production:

{scene_summary}

Calculate budget line items for:
- Crew (director, DP, AD, sound, etc.)
- Equipment rental (camera, lighting, grip, sound)
- Location fees
- Talent/casting
- Props and wardrobe
- Post-production (editing, color, sound mix)
- Insurance (5% of production costs)
- Contingency (12.5%)

Provide min/max ranges for each line item.
Include explicit assumptions and cost drivers.

Return as JSON matching BudgetEstimate schema.
"""
    
    try:
        # Increased max_tokens to 8000 to accommodate reasoning tokens + output
        budget_json = call_tamus_api(prompt, max_tokens=8000)
        # Extract JSON from response
        clean_json = extract_json_from_llm_response(budget_json)
        budget_estimate = json.loads(clean_json)
        total_min = budget_estimate.get("total_min", 0)
        total_max = budget_estimate.get("total_max", 0)
        print(f"✓ Generated budget estimate: ${total_min:,.0f} - ${total_max:,.0f}")
        return {"budget_estimate": budget_estimate, "overall_status": "Budget estimate created. "}
    except TimeoutError:
        print(f"⚠ API timeout - using synthetic budget data")
        budget_estimate = generate_synthetic_budget(scenes)
        return {"budget_estimate": budget_estimate, "overall_status": "Budget estimate created (synthetic). "}
    except (json.JSONDecodeError, Exception) as e:
        print(f"⚠ Error: {e} - using synthetic budget data")
        budget_estimate = generate_synthetic_budget(scenes)
        return {"budget_estimate": budget_estimate, "overall_status": "Budget estimate created (synthetic). "}


def schedule_ad_node(state: State) -> Dict:
    """Generate shoot schedule with days and company moves."""
    print("------ENTERING: SCHEDULE PLANNING NODE------")
    
    scene_plan = state.get("scene_plan", {})
    scenes = scene_plan.get("scenes", [])
    
    scenes_by_location = {}
    for scene in scenes:
        loc = scene.get("location_description", "Unknown")
        if loc not in scenes_by_location:
            scenes_by_location[loc] = []
        scenes_by_location[loc].append(scene.get("scene_id", ""))
    
    prompt = f"""You are a production scheduler. Generate a shoot schedule for these scenes:

Scenes by location:
{json.dumps(scenes_by_location, indent=2)}

Group scenes by location to minimize company moves.
Estimate setup time (0.5-2 hours) and shoot time (0.5-1 hour per scene).
Assume 10-12 hour shoot days.
Include company move time (1-3 hours) between locations.

Return as JSON matching SchedulePlan schema with schedule_days array and assumptions.
"""
    
    # Increased max_tokens to 8000 to accommodate reasoning tokens + output
    schedule_json = call_tamus_api(prompt, max_tokens=8000)
    
    try:
        # Extract JSON from response
        clean_json = extract_json_from_llm_response(schedule_json)
        schedule_plan = json.loads(clean_json)
        total_days = schedule_plan.get("total_shoot_days", 0)
        print(f"✓ Generated schedule: {total_days} shoot days")
        return {"schedule_plan": schedule_plan, "overall_status": "Schedule plan created. "}
    except json.JSONDecodeError as e:
        print(f"⚠ Error parsing schedule: {e}")
        print(f"  Response preview: {schedule_json[:200]}...")
        # Use synthetic schedule on parse failure
        schedule_plan = generate_synthetic_schedule(scenes)
        return {"schedule_plan": schedule_plan, "overall_status": "Schedule plan created (synthetic). "}


def casting_node(state: State) -> Dict:
    """Generate casting suggestions."""
    print("------ENTERING: CASTING NODE------")
    
    scene_plan = state.get("scene_plan", {})
    scenes = scene_plan.get("scenes", [])
    
    cast_summary = f"Total cast needed: {sum(s.get('cast_count', 0) for s in scenes)}"
    
    prompt = f"""Generate casting recommendations for this production:

{cast_summary}

Provide:
- Character breakdown with descriptions
- Age ranges and key attributes
- Casting approach (professional actors, non-actors, brand ambassadors)
- Special requirements (stunts, special skills)

Return as JSON with casting_breakdown array.
"""
    
    # Increased max_tokens to 6000 to accommodate reasoning tokens + output
    casting_json = call_tamus_api(prompt, max_tokens=6000)
    
    try:
        casting_suggestions = json.loads(casting_json)
        print(f"Generated casting suggestions")
        return {"casting_suggestions": casting_suggestions, "overall_status": "Casting suggestions created. "}
    except json.JSONDecodeError as e:
        print(f"Error parsing casting suggestions: {e}")
        return {"overall_status": f"Casting suggestions failed: {e}. "}


def props_wardrobe_node(state: State) -> Dict:
    """Generate props and wardrobe list."""
    print("------ENTERING: PROPS AND WARDROBE NODE------")
    
    scene_plan = state.get("scene_plan", {})
    scenes = scene_plan.get("scenes", [])
    
    all_props = []
    all_wardrobe = []
    for scene in scenes:
        all_props.extend(scene.get("props", []))
        all_wardrobe.extend(scene.get("wardrobe", []))
    
    prompt = f"""Generate a comprehensive props and wardrobe list:

Props: {', '.join(set(all_props))}
Wardrobe: {', '.join(set(all_wardrobe))}

For each item, provide:
- Quantity needed
- Source (purchase, rental, on-hand)
- Estimated cost
- Special handling notes

Return as JSON with props_list and wardrobe_list arrays.
"""
    
    # Increased max_tokens to 6000 to accommodate reasoning tokens + output
    props_wardrobe_json = call_tamus_api(prompt, max_tokens=6000)
    
    try:
        props_wardrobe_list = json.loads(props_wardrobe_json)
        print(f"Generated props and wardrobe list")
        return {"props_wardrobe_list": props_wardrobe_list, "overall_status": "Props/wardrobe list created. "}
    except json.JSONDecodeError as e:
        print(f"Error parsing props/wardrobe: {e}")
        return {"overall_status": f"Props/wardrobe list failed: {e}. "}


def crew_gear_node(state: State) -> Dict:
    """Generate crew and equipment recommendations."""
    print("------ENTERING: CREW AND GEAR NODE------")
    
    scene_plan = state.get("scene_plan", {})
    scenes = scene_plan.get("scenes", [])
    
    scene_complexity = len(scenes)
    
    prompt = f"""You are a production coordinator. Generate crew and equipment recommendations for this production:

Scene complexity: {scene_complexity} scenes

Provide:
1. Minimum viable crew list with roles and responsibilities
2. Minimum viable equipment list
3. Optional upgrades for crew and equipment (marked with required=False)

Base recommendations on scene complexity, location types, and technical requirements.

Return as JSON matching CrewGearPackage schema with crew and equipment arrays.
"""
    
    # Increased max_tokens to 8000 to accommodate reasoning tokens + output
    crew_gear_json = call_tamus_api(prompt, max_tokens=8000)
    
    try:
        # Extract JSON from response
        clean_json = extract_json_from_llm_response(crew_gear_json)
        crew_gear_package = json.loads(clean_json)
        print(f"✓ Generated crew and gear recommendations")
        return {"crew_gear": crew_gear_package, "overall_status": "Crew/gear package created. "}
    except json.JSONDecodeError as e:
        print(f"⚠ Error parsing crew/gear: {e}")
        print(f"  Response preview: {crew_gear_json[:200]}...")
        # Return minimal crew/gear
        return {
            "crew_gear": {
                "crew": [],
                "equipment": []
            },
            "overall_status": "Crew/gear parsing failed, using empty list. "
        }


def legal_clearance_node(state: State) -> Dict:
    """Generate legal clearances checklist."""
    print("------ENTERING: LEGAL CLEARANCE NODE------")
    
    scene_plan = state.get("scene_plan", {})
    scenes = scene_plan.get("scenes", [])
    
    total_cast = sum(s.get("cast_count", 0) for s in scenes)
    ext_scenes = [s for s in scenes if s.get("location_type") == "EXT"]
    
    prompt = f"""You are a legal compliance specialist. Generate legal clearances checklist for this production:

Total cast: {total_cast}
Exterior scenes: {len(ext_scenes)}

Identify:
- Talent releases required (based on cast count)
- Location releases required (based on location types)
- Trademark/logo clearances (scan scene descriptions)
- Music rights requirements
- Claims/substantiation requirements
- Minor involvement (requires parental consent)
- Drone permits (if aerial shots)

Mark high-risk items requiring legal review.

Return as JSON matching LegalClearanceReport schema with items array.
"""
    
    # Increased max_tokens to 8000 to accommodate reasoning tokens + output
    legal_json = call_tamus_api(prompt, max_tokens=8000)
    
    try:
        # Extract JSON from response
        clean_json = extract_json_from_llm_response(legal_json)
        legal_clearance_report = json.loads(clean_json)
        print(f"✓ Generated legal clearance report")
        return {"legal_clearances": legal_clearance_report, "overall_status": "Legal clearance report created. "}
    except json.JSONDecodeError as e:
        print(f"⚠ Error parsing legal clearance: {e}")
        print(f"  Response preview: {legal_json[:200]}...")
        # Return minimal legal clearances
        return {
            "legal_clearances": {
                "items": []
            },
            "overall_status": "Legal clearance parsing failed, using empty list. "
        }


def risk_safety_node(state: State) -> Dict:
    """Generate risk register with mitigation strategies."""
    print("------ENTERING: RISK AND SAFETY NODE------")
    
    scene_plan = state.get("scene_plan", {})
    scenes = scene_plan.get("scenes", [])
    
    ext_scenes = [s for s in scenes if s.get("location_type") == "EXT"]
    night_scenes = [s for s in scenes if s.get("time_of_day") == "NIGHT"]
    
    prompt = f"""You are a production safety coordinator. Generate risk and safety register for this production:

Exterior scenes: {len(ext_scenes)}
Night scenes: {len(night_scenes)}

Identify risks:
- Safety hazards (stunts, special effects, heights, water)
- Weather risks (for exterior scenes)
- Night shoot risks
- Stunt risks
- Crowd management risks (if cast > 10)
- Equipment risks

For each risk, provide:
- Likelihood (LOW/MEDIUM/HIGH)
- Impact (LOW/MEDIUM/HIGH)
- Mitigation strategy

Return as JSON matching RiskRegister schema with risks array.
"""
    
    # Increased max_tokens to 8000 to accommodate reasoning tokens + output
    risk_json = call_tamus_api(prompt, max_tokens=8000)
    
    try:
        # Extract JSON from response
        clean_json = extract_json_from_llm_response(risk_json)
        risk_register = json.loads(clean_json)
        print(f"✓ Generated risk register with {len(risk_register.get('risks', []))} risks")
        return {"risk_register": risk_register, "overall_status": "Risk register created. "}
    except json.JSONDecodeError as e:
        print(f"⚠ Error parsing risk register: {e}")
        print(f"  Response preview: {risk_json[:200]}...")
        # Return minimal risk register
        return {
            "risk_register": {
                "risks": []
            },
            "overall_status": "Risk register parsing failed, using empty list. "
        }


def budget_schedule_approval_gate(state: State) -> Dict:
    """Display budget and schedule for human approval (HITL gate)."""
    print("------ENTERING: BUDGET AND SCHEDULE APPROVAL GATE------")
    
    budget = state.get("budget_estimate", {})
    schedule = state.get("schedule_plan", {})
    
    print("\n=== BUDGET SUMMARY ===")
    print(f"Total Budget: ${budget.get('total_min', 0):,.0f} - ${budget.get('total_max', 0):,.0f}")
    print(f"Contingency: {budget.get('contingency_percent', 0)}%")
    
    print("\n=== SCHEDULE SUMMARY ===")
    print(f"Total Shoot Days: {schedule.get('total_shoot_days', 0)}")
    
    approval = input("\nApprove budget and schedule? (yes/no): ").lower()
    
    if approval == "yes":
        return {"overall_status": "Budget and schedule approved. "}
    else:
        return {"overall_status": "Budget and schedule rejected. "}


def client_review_pack_node(state: State) -> Dict:
    """Generate consolidated production pack markdown document."""
    print("------ENTERING: CLIENT REVIEW PACK GENERATION NODE------")
    
    brand_name = state.get("creative_brief", {}).get("brand_name", "Brand")
    theme = state.get("theme", "")
    budget = state.get("budget_estimate", {})
    schedule = state.get("schedule_plan", {})
    
    # Generate markdown document
    markdown_content = f"""# Production Pack: {brand_name} - {theme}

**Generated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Budget:** ${budget.get('total_min', 0):,.0f} - ${budget.get('total_max', 0):,.0f}
**Total Shoot Days:** {schedule.get('total_shoot_days', 0)}

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Concept](#concept)
3. [Screenplay](#screenplay)
4. [Storyboard](#storyboard)
5. [Scene Plan](#scene-plan)
6. [Locations Plan](#locations-plan)
7. [Budget Estimate](#budget-estimate)
8. [Schedule Plan](#schedule-plan)
9. [Crew and Gear](#crew-and-gear)
10. [Legal Clearances](#legal-clearances)
11. [Risk Register](#risk-register)

---

## Executive Summary

This production pack contains all planning artifacts for the {brand_name} advertisement campaign.

## Concept

{state.get('concept', 'N/A')}

## Screenplay

{state.get('screenplay_winner', 'N/A')}

## Storyboard

{state.get('story_board', 'N/A')}

## Scene Plan

{json.dumps(state.get('scene_plan', {}), indent=2)}

## Locations Plan

{json.dumps(state.get('locations_plan', {}), indent=2)}

## Budget Estimate

{json.dumps(state.get('budget_estimate', {}), indent=2)}

## Schedule Plan

{json.dumps(state.get('schedule_plan', {}), indent=2)}

## Crew and Gear

{json.dumps(state.get('crew_gear_package', {}), indent=2)}

## Legal Clearances

{json.dumps(state.get('legal_clearance_report', {}), indent=2)}

## Risk Register

{json.dumps(state.get('risk_register', {}), indent=2)}
"""
    
    # Save to file
    output_path = f"output/production_pack_{brand_name.replace(' ', '_')}.md"
    with open(output_path, 'w') as f:
        f.write(markdown_content)
    
    print(f"Production pack saved to: {output_path}")
    
    return {"production_pack": output_path, "overall_status": "Production pack generated. "}


# ============================================================================
# LANGGRAPH PIPELINE SETUP
# ============================================================================

def create_production_pipeline():
    """Create and configure the LangGraph production pipeline."""
    
    # Create workflow
    workflow = StateGraph(State)
    
    # Add creative chain nodes (preserved from original)
    workflow.add_node("ad_concept_creation_node", ad_concept_creation_node)
    workflow.add_node("screen_play_creation_in_rajamouli_style", screen_play_creation_node_1)
    workflow.add_node("screen_play_creation_in_shankar_style", screen_play_creation_node_2)
    workflow.add_node("screenplay_evaluation_node", screenplay_evaluation_node)
    workflow.add_node("story_board_creation_node", story_board_creation_node)
    
    # Add production planning nodes
    workflow.add_node("scene_breakdown_node", scene_breakdown_node)
    workflow.add_node("scene_plan_approval_gate", scene_plan_approval_gate)
    workflow.add_node("location_planning_node", location_planning_node)
    workflow.add_node("budgeting_node", budgeting_node)
    workflow.add_node("schedule_ad_node", schedule_ad_node)
    workflow.add_node("casting_node", casting_node)
    workflow.add_node("props_wardrobe_node", props_wardrobe_node)
    workflow.add_node("crew_gear_node", crew_gear_node)
    workflow.add_node("legal_clearance_node", legal_clearance_node)
    workflow.add_node("risk_safety_node", risk_safety_node)
    workflow.add_node("budget_schedule_approval_gate", budget_schedule_approval_gate)
    workflow.add_node("client_review_pack_node", client_review_pack_node)
    
    # Set entry point
    workflow.set_entry_point("ad_concept_creation_node")
    
    # Creative chain edges (preserved from original)
    workflow.add_edge("ad_concept_creation_node", "screen_play_creation_in_rajamouli_style")
    workflow.add_edge("ad_concept_creation_node", "screen_play_creation_in_shankar_style")
    workflow.add_edge("screen_play_creation_in_rajamouli_style", "screenplay_evaluation_node")
    workflow.add_edge("screen_play_creation_in_shankar_style", "screenplay_evaluation_node")
    workflow.add_edge("screenplay_evaluation_node", "story_board_creation_node")
    
    # Production planning edges
    workflow.add_edge("story_board_creation_node", "scene_breakdown_node")
    workflow.add_edge("scene_breakdown_node", "scene_plan_approval_gate")
    
    # Parallel planning nodes (fan-out from approval gate)
    workflow.add_edge("scene_plan_approval_gate", "location_planning_node")
    workflow.add_edge("scene_plan_approval_gate", "budgeting_node")
    workflow.add_edge("scene_plan_approval_gate", "schedule_ad_node")
    workflow.add_edge("scene_plan_approval_gate", "casting_node")
    workflow.add_edge("scene_plan_approval_gate", "props_wardrobe_node")
    workflow.add_edge("scene_plan_approval_gate", "crew_gear_node")
    workflow.add_edge("scene_plan_approval_gate", "legal_clearance_node")
    workflow.add_edge("scene_plan_approval_gate", "risk_safety_node")
    
    # Fan-in to budget/schedule approval gate
    workflow.add_edge("location_planning_node", "budget_schedule_approval_gate")
    workflow.add_edge("budgeting_node", "budget_schedule_approval_gate")
    workflow.add_edge("schedule_ad_node", "budget_schedule_approval_gate")
    workflow.add_edge("casting_node", "budget_schedule_approval_gate")
    workflow.add_edge("props_wardrobe_node", "budget_schedule_approval_gate")
    workflow.add_edge("crew_gear_node", "budget_schedule_approval_gate")
    workflow.add_edge("legal_clearance_node", "budget_schedule_approval_gate")
    workflow.add_edge("risk_safety_node", "budget_schedule_approval_gate")
    
    # Final production pack generation
    workflow.add_edge("budget_schedule_approval_gate", "client_review_pack_node")
    
    # Set finish point
    workflow.set_finish_point("client_review_pack_node")
    
    return workflow.compile()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=== Ad Production Pipeline ===\n")
    
    # Create pipeline
    production_graph = create_production_pipeline()
    
    # Example creative brief
    creative_brief = {
        "brand_name": "EcoPhone",
        "theme": "Sustainable technology for a better tomorrow",
        "target_duration_sec": 30,
        "aspect_ratio": "16:9"
    }
    
    # Initial state
    initial_state = {
        "theme": creative_brief["theme"],
        "creative_brief": creative_brief,
        "overall_status": ""
    }
    
    # Run pipeline
    print("Starting production pipeline...\n")
    final_state = production_graph.invoke(initial_state)
    
    print("\n=== PIPELINE COMPLETE ===")
    print(f"Status: {final_state.get('overall_status', '')}")
    print(f"Production Pack: {final_state.get('production_pack', 'N/A')}")
