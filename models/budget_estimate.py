"""
Budget Estimate Data Models

Defines TypedDict classes for budget estimation and line items.
"""

from typing import TypedDict, List


class BudgetLineItem(TypedDict):
    """Individual budget line item."""
    category: str
    item: str
    quantity: int
    unit_cost: float
    total_cost: float
    assumptions: str


class BudgetEstimate(TypedDict):
    """Complete budget estimate with line items and cost drivers."""
    total_min: float
    total_max: float
    line_items: List[BudgetLineItem]
    cost_drivers: List[str]
    contingency_percent: float
