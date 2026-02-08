"""
Scene Plan Data Models

Defines TypedDict classes for scene breakdown and shot planning.
"""

from typing import TypedDict, List


class Shot(TypedDict):
    """Individual shot within a scene."""
    shot_id: str
    scene_id: str
    shot_type: str  # "WIDE", "MEDIUM", "CLOSE-UP", "INSERT", "POV"
    camera_movement: str  # "STATIC", "PAN", "TILT", "DOLLY", "STEADICAM"
    duration_sec: float
    description: str


class SceneDetail(TypedDict):
    """Detailed scene information."""
    scene_id: str
    duration_sec: float
    location_type: str  # "INT" or "EXT"
    time_of_day: str  # "DAY" or "NIGHT"
    location_description: str
    cast_count: int
    props: List[str]
    wardrobe: List[str]
    sfx_vfx: List[str]
    dialogue_vo: str
    on_screen_text: str


class ScenePlan(TypedDict):
    """Complete scene plan with scenes and shots."""
    scenes: List[SceneDetail]
    shots: List[Shot]
