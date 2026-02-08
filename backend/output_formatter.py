"""
Output Formatter for LLM-generated content
Parses and structures raw LLM outputs into clean, readable formats
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import re


class ConceptOutput(BaseModel):
    """Structured concept output"""
    title: str = Field(description="Concept title")
    core_idea: str = Field(description="Core creative idea")
    story_beats: List[Dict[str, str]] = Field(default_factory=list, description="Story beats with timing")
    why_it_works: List[str] = Field(default_factory=list, description="Justification points")
    visual_direction: Dict[str, str] = Field(default_factory=dict, description="Visual and sound direction")
    budget_notes: Optional[str] = Field(None, description="Budget considerations")
    brand_elements: List[str] = Field(default_factory=list, description="Brand integration points")
    key_message: str = Field(description="Core message")


class SceneOutput(BaseModel):
    """Structured scene output"""
    scene_number: int
    duration: int
    title: Optional[str] = None
    visuals: str = Field(description="Visual description")
    action: str = Field(description="Action description")
    camera: Optional[str] = Field(None, description="Camera direction")
    dialogue: Optional[str] = Field(None, description="Dialogue")
    text_on_screen: Optional[str] = Field(None, description="On-screen text")


class ScreenplayOutput(BaseModel):
    """Structured screenplay output"""
    title: str
    genre: Optional[str] = None
    setting: Optional[str] = None
    characters: List[str] = Field(default_factory=list)
    plot_overview: Optional[str] = None
    scenes: List[SceneOutput]
    total_duration: int = 0


def parse_concept(raw_text: str) -> ConceptOutput:
    """
    Parse raw concept text into structured format
    
    Args:
        raw_text: Raw LLM output
        
    Returns:
        Structured ConceptOutput
    """
    lines = raw_text.split('\n')
    
    # Extract title
    title = "Untitled Concept"
    for line in lines[:10]:
        if 'title' in line.lower() or line.startswith('#'):
            title = re.sub(r'^#+\s*|\*\*|Title:\s*', '', line).strip()
            if title:
                break
    
    # Extract core idea
    core_idea = ""
    in_core = False
    for line in lines:
        if 'core idea' in line.lower() or 'core concept' in line.lower():
            in_core = True
            continue
        if in_core and line.strip() and not line.startswith('#'):
            core_idea += line.strip() + " "
            if len(core_idea) > 200:
                break
    
    # Extract story beats
    story_beats = []
    in_beats = False
    current_beat = {}
    for line in lines:
        if '30-second story' in line.lower() or 'story beats' in line.lower():
            in_beats = True
            continue
        if in_beats and re.match(r'\*\*\d+:\d+', line):
            if current_beat:
                story_beats.append(current_beat)
            timing = re.search(r'(\d+:\d+[–-]\d+:\d+)', line)
            title_match = re.search(r'\|\s*(.+?)\s*\*\*', line)
            current_beat = {
                'timing': timing.group(1) if timing else '',
                'title': title_match.group(1) if title_match else '',
                'description': ''
            }
        elif in_beats and current_beat and line.strip() and not line.startswith('#'):
            current_beat['description'] += line.strip() + " "
    
    if current_beat:
        story_beats.append(current_beat)
    
    # Extract "why it works"
    why_it_works = []
    in_why = False
    for line in lines:
        if 'why this works' in line.lower() or 'justification' in line.lower():
            in_why = True
            continue
        if in_why and line.strip().startswith(('1.', '2.', '3.', '4.', '-', '•')):
            point = re.sub(r'^\d+\.\s*|\*\*|-|•', '', line).strip()
            if point:
                why_it_works.append(point)
    
    # Extract visual direction
    visual_direction = {}
    for line in lines:
        if 'palette:' in line.lower():
            visual_direction['palette'] = re.sub(r'.*palette:\s*', '', line, flags=re.IGNORECASE).strip()
        elif 'cinematography:' in line.lower():
            visual_direction['cinematography'] = re.sub(r'.*cinematography:\s*', '', line, flags=re.IGNORECASE).strip()
        elif 'sound:' in line.lower():
            visual_direction['sound'] = re.sub(r'.*sound:\s*', '', line, flags=re.IGNORECASE).strip()
    
    # Extract key message
    key_message = ""
    for line in lines:
        if 'key line' in line.lower() or 'key message' in line.lower():
            key_message = re.sub(r'.*:\s*\*?', '', line).strip().strip('*"')
            break
    
    return ConceptOutput(
        title=title,
        core_idea=core_idea.strip(),
        story_beats=story_beats,
        why_it_works=why_it_works,
        visual_direction=visual_direction,
        key_message=key_message or "Sustainable innovation meets premium design"
    )


def parse_screenplay(raw_text: str, variant_name: str = "Screenplay") -> ScreenplayOutput:
    """
    Parse raw screenplay text into structured format
    
    Args:
        raw_text: Raw LLM output
        variant_name: Name of the screenplay variant
        
    Returns:
        Structured ScreenplayOutput
    """
    print(f"\n[OUTPUT_FORMATTER] Parsing screenplay: {variant_name}")
    print(f"[OUTPUT_FORMATTER] Raw text length: {len(raw_text)} characters")
    print(f"[OUTPUT_FORMATTER] First 800 characters:")
    print(raw_text[:800])
    print("[OUTPUT_FORMATTER] ---")
    
    lines = raw_text.split('\n')
    
    # Extract title
    title = variant_name
    for line in lines[:10]:
        if 'title:' in line.lower():
            title = re.sub(r'.*title:\s*', '', line, flags=re.IGNORECASE).strip()
            # Remove markdown bold markers
            title = title.replace('**', '').strip()
            break
    
    # Extract genre
    genre = None
    for line in lines[:20]:
        if 'genre:' in line.lower():
            genre = re.sub(r'.*genre:\s*', '', line, flags=re.IGNORECASE).strip()
            # Remove markdown bold markers
            genre = genre.replace('**', '').strip()
            break
    
    # Parse scenes
    scenes = []
    current_scene = None
    current_field = None
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check if this is a scene header - handle multiple formats:
        # - "SCENE 1" or "Scene 1"
        # - "## Scene 1" or "### 1)"
        # - "### 1) OPENING — MODERN VAULT (0:00–0:04)"
        is_scene_header = False
        
        # Pattern 1: Starts with SCENE/Scene
        if re.match(r'^(SCENE|Scene)\s+\d+', line_stripped, re.IGNORECASE):
            is_scene_header = True
        # Pattern 2: Starts with ## or ###
        elif line_stripped.startswith(('##', '###')):
            is_scene_header = True
        
        if is_scene_header:
            # Save previous scene
            if current_scene and current_scene.get('visuals'):
                print(f"[OUTPUT_FORMATTER] Found scene {current_scene['scene_number']}: {current_scene['visuals'][:100]}...")
                scenes.append(SceneOutput(
                    scene_number=current_scene['scene_number'],
                    duration=current_scene['duration'],
                    title=current_scene.get('title'),
                    visuals=current_scene['visuals'],
                    action=current_scene.get('action', ''),
                    camera=current_scene.get('camera'),
                    dialogue=current_scene.get('dialogue'),
                    text_on_screen=current_scene.get('text_on_screen')
                ))
            
            # Start new scene - extract scene number and duration
            # Try multiple duration formats:
            # - "### 1) TITLE (0:00–0:04)" -> duration is 4 seconds (end time)
            # - "Scene 1 (5s)" -> duration is 5 seconds
            # - "Scene 1 (6 seconds)" -> duration is 6 seconds
            
            scene_num = None
            duration = 5  # default
            
            # Extract scene number
            num_match = re.search(r'(\d+)', line_stripped)
            if num_match:
                scene_num = int(num_match.group(1))
            else:
                scene_num = len(scenes) + 1
            
            # Try to extract duration - multiple patterns
            # Pattern 1: (0:00–0:04) or (0:00-0:04) -> extract end time
            time_range_match = re.search(r'\([\d:]+[–-]([\d:]+)\)', line_stripped)
            if time_range_match:
                end_time = time_range_match.group(1)
                # Parse time format like "0:04" or "0:10"
                time_parts = end_time.split(':')
                if len(time_parts) == 2:
                    minutes = int(time_parts[0])
                    seconds = int(time_parts[1])
                    duration = minutes * 60 + seconds
            else:
                # Pattern 2: (5s) or (6 seconds)
                duration_match = re.search(r'\((\d+)\s*s(?:econds?)?\)', line_stripped)
                if duration_match:
                    duration = int(duration_match.group(1))
            
            current_scene = {
                'scene_number': scene_num,
                'duration': duration,
                'visuals': '',
                'action': '',
                'camera': '',
                'dialogue': '',
                'text_on_screen': ''
            }
            print(f"[OUTPUT_FORMATTER] Starting scene {scene_num} (duration: {duration}s)")
            current_field = None
            continue
        
        if not current_scene or not line_stripped:
            continue
        
        # Check for field labels - handle both plain and markdown bold formats
        # Remove markdown bold (**) before checking
        line_clean = line_stripped.replace('**', '')
        line_lower = line_clean.lower()
        
        if line_lower.startswith(('visual:', 'visuals:')):
            current_field = 'visuals'
            content = re.sub(r'^\*?\*?visuals?:\*?\*?\s*', '', line_stripped, flags=re.IGNORECASE)
            # Remove any remaining markdown bold markers
            content = content.replace('**', '')
            if content:
                current_scene['visuals'] += content + ' '
        elif line_lower.startswith('action:'):
            current_field = 'action'
            content = re.sub(r'^\*?\*?action:\*?\*?\s*', '', line_stripped, flags=re.IGNORECASE)
            content = content.replace('**', '')
            if content:
                current_scene['action'] += content + ' '
        elif line_lower.startswith(('camera:', 'camera transition:')):
            current_field = 'camera'
            content = re.sub(r'^\*?\*?camera.*?:\*?\*?\s*', '', line_stripped, flags=re.IGNORECASE)
            content = content.replace('**', '')
            if content:
                current_scene['camera'] += content + ' '
        elif line_lower.startswith(('dialogue:', 'dialog:')):
            current_field = 'dialogue'
            # Remove both the field label and any markdown
            content = re.sub(r'^\*?\*?dialou?ge?:\*?\*?\s*', '', line_stripped, flags=re.IGNORECASE)
            content = content.replace('**', '').replace('Dialogue:', '').replace('Dialog:', '').strip()
            if content:
                current_scene['dialogue'] += content + ' '
        elif line_lower.startswith(('text on screen:', 'text:')):
            current_field = 'text_on_screen'
            content = re.sub(r'^\*?\*?text.*?:\*?\*?\s*', '', line_stripped, flags=re.IGNORECASE)
            content = content.replace('**', '')
            if content:
                current_scene['text_on_screen'] += content + ' '
        elif line_lower.startswith('close-up:') or line_lower.startswith('close up:'):
            # Add close-up to visuals field
            current_field = 'visuals'
            content = re.sub(r'^\*?\*?close-?up:\*?\*?\s*', '', line_stripped, flags=re.IGNORECASE)
            content = content.replace('**', '')
            if content:
                current_scene['visuals'] += 'Close-up: ' + content + ' '
        elif current_field and line_stripped:
            # Continue adding to current field - remove markdown
            clean_content = line_stripped.replace('**', '')
            current_scene[current_field] += clean_content + ' '
    
    # Add last scene
    if current_scene and current_scene.get('visuals'):
        print(f"[OUTPUT_FORMATTER] Found scene {current_scene['scene_number']}: {current_scene['visuals'][:100]}...")
        scenes.append(SceneOutput(
            scene_number=current_scene['scene_number'],
            duration=current_scene['duration'],
            title=current_scene.get('title'),
            visuals=current_scene['visuals'].strip(),
            action=current_scene.get('action', '').strip(),
            camera=current_scene.get('camera', '').strip(),
            dialogue=current_scene.get('dialogue', '').strip(),
            text_on_screen=current_scene.get('text_on_screen', '').strip()
        ))
    
    print(f"[OUTPUT_FORMATTER] Total scenes parsed: {len(scenes)}")
    
    # Only add placeholders if we have very few scenes (less than 3)
    if len(scenes) < 3:
        print(f"[OUTPUT_FORMATTER] WARNING: Only found {len(scenes)} scenes, adding {6 - len(scenes)} placeholder scenes")
        while len(scenes) < 6:
            scene_num = len(scenes) + 1
            scenes.append(SceneOutput(
                scene_number=scene_num,
                duration=5,
                visuals=f"Scene {scene_num}: Cinematic visual sequence",
                action="Dynamic action and movement",
                camera="Medium shot with smooth camera movement"
            ))
    elif len(scenes) < 6:
        print(f"[OUTPUT_FORMATTER] Note: Found {len(scenes)} scenes (expected 6), but this is acceptable")
    
    total_duration = sum(s.duration for s in scenes)
    
    return ScreenplayOutput(
        title=title,
        genre=genre,
        scenes=scenes[:6],  # Limit to 6 scenes
        total_duration=total_duration
    )


def format_concept_for_display(concept: ConceptOutput) -> str:
    """
    Format structured concept into clean, readable text
    
    Args:
        concept: Structured concept data
        
    Returns:
        Formatted markdown text
    """
    output = f"# {concept.title}\n\n"
    
    if concept.core_idea:
        output += f"## Core Idea\n\n{concept.core_idea}\n\n"
    
    if concept.story_beats:
        output += "## Story Beats\n\n"
        for beat in concept.story_beats:
            output += f"**{beat.get('timing', '')} | {beat.get('title', '')}**\n\n"
            output += f"{beat.get('description', '')}\n\n"
    
    if concept.why_it_works:
        output += "## Why This Works\n\n"
        for i, point in enumerate(concept.why_it_works, 1):
            output += f"{i}. {point}\n\n"
    
    if concept.visual_direction:
        output += "## Visual & Sound Direction\n\n"
        for key, value in concept.visual_direction.items():
            output += f"**{key.title()}:** {value}\n\n"
    
    if concept.key_message:
        output += f"## Key Message\n\n*\"{concept.key_message}\"*\n\n"
    
    return output


def format_screenplay_for_display(screenplay: ScreenplayOutput) -> str:
    """
    Format structured screenplay into clean, readable text
    
    Args:
        screenplay: Structured screenplay data
        
    Returns:
        Formatted markdown text
    """
    output = f"# {screenplay.title}\n\n"
    
    if screenplay.genre:
        output += f"**Genre:** {screenplay.genre}\n\n"
    
    if screenplay.setting:
        output += f"**Setting:** {screenplay.setting}\n\n"
    
    output += f"**Total Duration:** {screenplay.total_duration} seconds\n\n"
    output += "---\n\n"
    
    for scene in screenplay.scenes:
        output += f"## Scene {scene.scene_number}"
        if scene.title:
            output += f": {scene.title}"
        output += f" ({scene.duration}s)\n\n"
        
        if scene.visuals:
            output += f"**Visuals:** {scene.visuals}\n\n"
        
        if scene.action:
            output += f"**Action:** {scene.action}\n\n"
        
        if scene.camera:
            output += f"**Camera:** {scene.camera}\n\n"
        
        if scene.dialogue:
            output += f"**Dialogue:** {scene.dialogue}\n\n"
        
        if scene.text_on_screen:
            output += f"**Text on Screen:** {scene.text_on_screen}\n\n"
        
        output += "---\n\n"
    
    return output
