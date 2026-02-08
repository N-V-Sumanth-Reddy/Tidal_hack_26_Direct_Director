"""
Crew and Gear Data Models

Defines TypedDict classes for crew and equipment recommendations.
"""

from typing import TypedDict, List


class CrewMember(TypedDict):
    """Crew member specification."""
    role: str
    responsibilities: str
    required: bool  # True for minimum viable, False for upgrades


class EquipmentItem(TypedDict):
    """Equipment item specification."""
    item: str
    quantity: int
    required: bool  # True for minimum viable, False for upgrades


class CrewGearPackage(TypedDict):
    """Complete crew and gear package."""
    crew: List[CrewMember]
    equipment: List[EquipmentItem]
