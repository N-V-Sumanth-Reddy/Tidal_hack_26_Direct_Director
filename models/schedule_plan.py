"""
Schedule Plan Data Models

Defines TypedDict classes for shoot scheduling.
"""

from typing import TypedDict, List, Optional


class ScheduleDay(TypedDict):
    """Individual shoot day schedule."""
    day_number: int
    date: Optional[str]
    location: str
    scenes: List[str]  # scene_ids
    setup_time_hours: float
    shoot_time_hours: float
    company_move_time_hours: float
    notes: str


class SchedulePlan(TypedDict):
    """Complete shoot schedule with days and assumptions."""
    total_shoot_days: int
    schedule_days: List[ScheduleDay]
    assumptions: List[str]
