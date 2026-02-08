"""
Legal Clearance Data Models

Defines TypedDict classes for legal clearances and compliance.
"""

from typing import TypedDict, List


class LegalItem(TypedDict):
    """Individual legal clearance item."""
    category: str  # "talent_release", "location_release", "trademark", "music", etc.
    description: str
    required: bool
    high_risk: bool


class LegalClearanceReport(TypedDict):
    """Complete legal clearance report."""
    items: List[LegalItem]
    minors_involved: bool
    drone_permits_required: bool
