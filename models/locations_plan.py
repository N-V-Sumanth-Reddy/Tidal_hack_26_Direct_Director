"""
Locations Plan Data Models

Defines TypedDict classes for location planning and requirements.
"""

from typing import TypedDict, List


class LocationRequirement(TypedDict):
    """Location requirement specification."""
    location_id: str
    location_type: str  # "INT" or "EXT"
    description: str
    key_features: List[str]
    accessibility_requirements: str
    power_requirements: str
    space_requirements: str
    alternates: List[str]


class LocationsPlan(TypedDict):
    """Complete locations plan with requirements and constraints."""
    locations: List[LocationRequirement]
    permits_required: List[str]
    noise_restrictions: bool
    time_restrictions: str
    parking_availability: str
    insurance_requirements: str
