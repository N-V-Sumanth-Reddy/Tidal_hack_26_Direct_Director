"""
Pipeline Integration for Backend

Integrates ad_production_pipeline_web.py with the FastAPI backend.
Provides step-by-step execution with caching.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

import asyncio
from typing import Dict, Any, Optional
from ad_production_pipeline_web import (
    ad_concept_creation_node,
    screen_play_creation_node_1,
    screen_play_creation_node_2,
    story_board_creation_node,
    scene_breakdown_node,
    production_planning_node
)


class PipelineRunner:
    """Manages step-by-step pipeline execution for web API."""
    
    def __init__(self):
        self.state_cache: Dict[str, Dict[str, Any]] = {}
        print("✓ Pipeline runner initialized")
    
    def _get_or_create_state(self, project_id: str, creative_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Get cached state or create new one."""
        if project_id not in self.state_cache:
            self.state_cache[project_id] = {
                "theme": creative_brief.get("theme", ""),
                "creative_brief": creative_brief,
                "overall_status": ""
            }
        return self.state_cache[project_id]
    
    async def generate_concept(self, project_id: str, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Generate concept from brief."""
        loop = asyncio.get_event_loop()
        
        # Get or create state
        state = self._get_or_create_state(project_id, brief)
        
        # Run concept node
        result = await loop.run_in_executor(None, ad_concept_creation_node, state)
        
        # Update cached state
        state.update(result)
        
        return {
            "concept": result.get("concept", ""),
            "status": "completed"
        }
    
    async def generate_screenplays(self, project_id: str, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Generate both screenplay variants."""
        loop = asyncio.get_event_loop()
        
        # Get state (should have concept already)
        state = self._get_or_create_state(project_id, brief)
        
        if not state.get("concept"):
            # Generate concept first if missing
            concept_result = await self.generate_concept(project_id, brief)
            state["concept"] = concept_result["concept"]
        
        # Run both screenplay nodes
        result1 = await loop.run_in_executor(None, screen_play_creation_node_1, state)
        state.update(result1)
        
        result2 = await loop.run_in_executor(None, screen_play_creation_node_2, state)
        state.update(result2)
        
        return {
            "screenplay_1": result1.get("screenplay_1", ""),
            "screenplay_2": result2.get("screenplay_2", ""),
            "status": "completed"
        }
    
    async def select_screenplay(self, project_id: str, screenplay_id: str) -> Dict[str, Any]:
        """Select winning screenplay."""
        if project_id not in self.state_cache:
            return {"status": "error", "message": "Project state not found"}
        
        state = self.state_cache[project_id]
        
        # Set winner based on selection
        if screenplay_id == "1" or "rajamouli" in screenplay_id.lower():
            state["screenplay_winner"] = state.get("screenplay_1", "")
        else:
            state["screenplay_winner"] = state.get("screenplay_2", "")
        
        return {"status": "completed"}
    
    async def generate_storyboard(self, project_id: str, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Generate storyboard with Gemini images."""
        loop = asyncio.get_event_loop()
        
        # Get state (should have screenplay_winner)
        state = self._get_or_create_state(project_id, brief)
        
        if not state.get("screenplay_winner"):
            # Generate screenplays and auto-select if missing
            await self.generate_screenplays(project_id, brief)
            state["screenplay_winner"] = state.get("screenplay_1", "")
        
        # Run storyboard node (includes Gemini image generation)
        result = await loop.run_in_executor(None, story_board_creation_node, state)
        state.update(result)
        
        return {
            "storyboard": result.get("story_board", ""),
            "storyboard_frames": result.get("storyboard_frames", []),
            "status": "completed"
        }
    
    async def generate_production_pack(self, project_id: str, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete production pack."""
        loop = asyncio.get_event_loop()
        
        # Get state (should have storyboard)
        state = self._get_or_create_state(project_id, brief)
        
        if not state.get("story_board"):
            # Generate storyboard first if missing
            await self.generate_storyboard(project_id, brief)
        
        # Run scene breakdown
        scene_result = await loop.run_in_executor(None, scene_breakdown_node, state)
        state.update(scene_result)
        
        # Run production planning
        prod_result = await loop.run_in_executor(None, production_planning_node, state)
        state.update(prod_result)
        
        return {
            "budget": prod_result.get("budget_estimate", {}),
            "schedule": prod_result.get("schedule_plan", {}),
            "locations": prod_result.get("locations_plan", {}),
            "crew": prod_result.get("crew_gear_package", {}),
            "legal": prod_result.get("legal_clearance_report", {}),
            "risks": prod_result.get("risk_register", {}),
            "status": "completed"
        }
    
    def clear_cache(self, project_id: str):
        """Clear cached state for a project."""
        if project_id in self.state_cache:
            del self.state_cache[project_id]


# Global pipeline runner instance
_pipeline_runner: Optional[PipelineRunner] = None


def get_pipeline_runner() -> PipelineRunner:
    """Get or create the global pipeline runner."""
    global _pipeline_runner
    if _pipeline_runner is None:
        _pipeline_runner = PipelineRunner()
    return _pipeline_runner

