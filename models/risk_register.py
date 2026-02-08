"""
Risk Register Data Models

Defines TypedDict classes for risk assessment and mitigation.
"""

from typing import TypedDict, List


class Risk(TypedDict):
    """Individual risk item."""
    risk_id: str
    category: str  # "safety", "weather", "night_shoot", "stunt", "crowd", "equipment"
    description: str
    likelihood: str  # "LOW", "MEDIUM", "HIGH"
    impact: str  # "LOW", "MEDIUM", "HIGH"
    mitigation_strategy: str


class RiskRegister(TypedDict):
    """Complete risk register."""
    risks: List[Risk]
