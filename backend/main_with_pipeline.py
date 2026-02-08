"""
FastAPI Backend with Full Production Pipeline Integration
Includes Gemini 2.5 Flash for storyboard image generation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import asyncio
import json
import uuid
import sys
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(parent_dir, '.env')

if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"✓ Loaded environment variables from: {env_path}")
    print(f"  - GEMINI_API_KEY: {'✓ Set' if os.getenv('GEMINI_API_KEY') else '✗ Not set'}")
    print(f"  - TAMUS_API_KEY: {'✓ Set' if os.getenv('TAMUS_API_KEY') else '✗ Not set'}")

sys.path.insert(0, parent_dir)

# Import pipeline integration
try:
    from backend.pipeline_integration import get_pipeline_runner
    PIPELINE_AVAILABLE = True
    print("✓ Successfully imported pipeline integration")
except Exception as e:
    print(f"✗ Warning: Could not import pipeline: {e}")
    PIPELINE_AVAILABLE = False

# Import TAMUS for fallback
try:
    from tamus_wrapper import get_tamus_client
    TAMUS_AVAILABLE = True
    print("✓ Successfully imported TAMUS wrapper")
except Exception as e:
    print(f"✗ Warning: Could not import TAMUS: {e}")
    TAMUS_AVAILABLE = False

# ============================================================================
# FastAPI App Setup
# ============================================================================

app = FastAPI(
    title="Virtual Ad Agency API (with Pipeline)",
    description="AI-powered ad production pipeline with Gemini images",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:2500", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Data Models
# ============================================================================

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    ARCHIVED = "archived"

class WorkflowStep(str, Enum):
    BRIEF = "brief"
    CONCEPT = "concept"
    SCREENPLAYS = "screenplays"
    SELECT = "select"
    STORYBOARD = "storyboard"
    PRODUCTION = "production"
    EXPORT = "export"

class BudgetBand(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PREMIUM = "premium"

class Brief(BaseModel):
    platform: str
    duration: int
    budget: float
    location: str
    constraints: List[str] = []
    creativeDirection: str
    brandMandatories: List[str] = []
    targetAudience: str

class CreateProjectRequest(BaseModel):
    name: str
    client: str
    tags: List[str] = []
    budgetBand: BudgetBand

class SubmitBriefRequest(BaseModel):
    brief: Brief

class SelectScreenplayRequest(BaseModel):
    screenplayId: str

# ============================================================================
# Storage
# ============================================================================

projects_db: Dict[str, Dict[str, Any]] = {}
jobs_db: Dict[str, Dict[str, Any]] = {}

# ============================================================================
# Helper Functions
# ============================================================================

def create_job(project_id: str, step: str) -> Dict[str, Any]:
    """Create a new generation job"""
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "project_id": project_id,
        "step": step,
        "status": "pending",
        "progress": 0,
        "started_at": datetime.now().isoformat(),
        "estimated_time": 60,
        "estimated_cost": 0.50,
    }
    jobs_db[job_id] = job
    return job

async def run_generation_with_pipeline(job_id: str, project_id: str, step: str, params: Dict[str, Any]):
    """Run generation using full pipeline with Gemini images"""
    job = jobs_db[job_id]
    project = projects_db[project_id]
    
    try:
        job["status"] = "running"
        job["progress"] = 10
        
        if not PIPELINE_AVAILABLE:
            raise Exception("Pipeline not available")
        
        pipeline = get_pipeline_runner()
        brief = project.get("brief", {})
        
        print(f"\n{'='*60}")
        print(f"🚀 Starting PIPELINE generation: {step}")
        print(f"Project: {project_id}")
        print(f"{'='*60}\n")
        
        if step == "concept":
            job["progress"] = 30
            result = await pipeline.generate_concept(project_id, brief)
            
            project["concept"] = {
                "id": str(uuid.uuid4()),
                "title": result.get("concept", "")[:100],
                "description": result.get("concept", ""),
                "keyMessage": brief.get("creativeDirection", ""),
                "visualStyle": "AI Generated",
                "generatedAt": datetime.now().isoformat(),
                "version": 1
            }
            print(f"✓ Concept generated via pipeline")
            
        elif step == "screenplays":
            job["progress"] = 30
            result = await pipeline.generate_screenplays(project_id, brief)
            
            # Parse screenplays from pipeline output
            screenplay_1 = result.get("screenplay_1", "")
            screenplay_2 = result.get("screenplay_2", "")
            
            def parse_scenes(text):
                scenes = []
                lines = text.split('\n')
                current_scene = None
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('SCENE') or line.startswith('Scene'):
                        if current_scene:
                            scenes.append(current_scene)
                        import re
                        match = re.search(r'(\d+).*?\((\d+)s?\)', line)
                        if match:
                            current_scene = {
                                "sceneNumber": int(match.group(1)),
                                "duration": int(match.group(2)),
                                "description": ""
                            }
                        else:
                            current_scene = {
                                "sceneNumber": len(scenes) + 1,
                                "duration": 6,
                                "description": ""
                            }
                    elif current_scene and line:
                        current_scene["description"] += line + " "
                
                if current_scene:
                    scenes.append(current_scene)
                
                while len(scenes) < 5:
                    scenes.append({
                        "sceneNumber": len(scenes) + 1,
                        "duration": 6,
                        "description": f"Scene {len(scenes) + 1} description"
                    })
                
                return scenes[:5]
            
            scenes_a = parse_scenes(screenplay_1)
            scenes_b = parse_scenes(screenplay_2)
            
            project["screenplays"] = [
                {
                    "id": str(uuid.uuid4()),
                    "variant": "A (Rajamouli Style)",
                    "scenes": scenes_a,
                    "totalDuration": sum(s.get("duration", 6) for s in scenes_a),
                    "scores": {"clarity": 8.5, "feasibility": 7.5, "costRisk": 6.5},
                    "generatedAt": datetime.now().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "variant": "B (Shankar Style)",
                    "scenes": scenes_b,
                    "totalDuration": sum(s.get("duration", 6) for s in scenes_b),
                    "scores": {"clarity": 7.8, "feasibility": 8.2, "costRisk": 7.0},
                    "generatedAt": datetime.now().isoformat()
                }
            ]
            print(f"✓ Screenplays generated via pipeline")
            
        elif step == "storyboard":
            job["progress"] = 30
            
            # Select screenplay for pipeline
            screenplays = project.get("screenplays", [])
            selected_id = project.get("selectedScreenplay")
            selected_screenplay = next((s for s in screenplays if s["id"] == selected_id), screenplays[0] if screenplays else None)
            
            if selected_screenplay:
                # Use pipeline to generate storyboard with Gemini images
                result = await pipeline.generate_storyboard(project_id, brief)
                
                storyboard_frames = result.get("storyboard_frames", [])
                scenes = selected_screenplay.get("scenes", [])
                
                storyboard_scenes = []
                for i, scene in enumerate(scenes):
                    frame = storyboard_frames[i] if i < len(storyboard_frames) else {}
                    storyboard_scenes.append({
                        "id": str(uuid.uuid4()),
                        "sceneNumber": scene.get("sceneNumber", i + 1),
                        "duration": scene.get("duration", 6),
                        "description": scene.get("description", ""),
                        "dialogue": None,
                        "cameraAngle": "Medium shot",
                        "notes": "AI generated with Gemini 2.5 Flash",
                        "imageUrl": frame.get("image_url")  # Gemini-generated image!
                    })
                
                project["storyboard"] = {
                    "id": str(uuid.uuid4()),
                    "generatedAt": datetime.now().isoformat(),
                    "scenes": storyboard_scenes
                }
                print(f"✓ Storyboard generated via pipeline with {len([s for s in storyboard_scenes if s['imageUrl']])} Gemini images")
            
        elif step == "production":
            job["progress"] = 30
            result = await pipeline.generate_production_pack(project_id, brief)
            
            project["productionPack"] = {
                "id": str(uuid.uuid4()),
                "generatedAt": datetime.now().isoformat(),
                "budget": result.get("budget", {}),
                "schedule": result.get("schedule", {}),
                "crew": result.get("crew", []),
                "locations": result.get("locations", []),
                "equipment": result.get("equipment", []),
                "legal": []
            }
            print(f"✓ Production pack generated via pipeline")
        
        job["progress"] = 100
        job["status"] = "completed"
        job["completed_at"] = datetime.now().isoformat()
        
        print(f"\n{'='*60}")
        print(f"✅ Pipeline generation completed: {step}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)
        print(f"\n✗ Pipeline generation failed: {e}")
        import traceback
        traceback.print_exc()

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Virtual Ad Agency API with Pipeline",
        "pipeline_available": PIPELINE_AVAILABLE,
        "gemini_enabled": os.getenv('GEMINI_API_KEY') is not None
    }

@app.get("/api/projects")
async def list_projects():
    return list(projects_db.values())

@app.post("/api/projects")
async def create_project(request: CreateProjectRequest):
    project_id = str(uuid.uuid4())
    project = {
        "id": project_id,
        "name": request.name,
        "client": request.client,
        "status": ProjectStatus.DRAFT,
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "currentStep": WorkflowStep.BRIEF,
        "tags": request.tags,
        "budgetBand": request.budgetBand,
    }
    projects_db[project_id] = project
    return project

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects_db[project_id]

@app.patch("/api/projects/{project_id}")
async def update_project(project_id: str, updates: Dict[str, Any]):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    project = projects_db[project_id]
    project.update(updates)
    project["updatedAt"] = datetime.now().isoformat()
    return project

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    del projects_db[project_id]
    return {"message": "Project deleted"}

@app.post("/api/projects/{project_id}/brief")
async def submit_brief(project_id: str, request: SubmitBriefRequest):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    project = projects_db[project_id]
    project["brief"] = request.brief.model_dump()
    project["currentStep"] = WorkflowStep.CONCEPT
    project["updatedAt"] = datetime.now().isoformat()
    return project

@app.post("/api/projects/{project_id}/generate/concept")
async def generate_concept(project_id: str, background_tasks: BackgroundTasks):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    project = projects_db[project_id]
    if "brief" not in project:
        raise HTTPException(status_code=400, detail="Brief not submitted")
    
    job = create_job(project_id, "concept")
    background_tasks.add_task(run_generation_with_pipeline, job["id"], project_id, "concept", {"brief": project["brief"]})
    
    return {"jobId": job["id"], "estimatedTime": job["estimated_time"], "estimatedCost": job["estimated_cost"]}

@app.post("/api/projects/{project_id}/generate/screenplays")
async def generate_screenplays(project_id: str, background_tasks: BackgroundTasks):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    project = projects_db[project_id]
    if "concept" not in project:
        raise HTTPException(status_code=400, detail="Concept not generated")
    
    job = create_job(project_id, "screenplays")
    background_tasks.add_task(run_generation_with_pipeline, job["id"], project_id, "screenplays", {"conceptId": project["concept"]["id"]})
    
    return {"jobId": job["id"], "estimatedTime": job["estimated_time"], "estimatedCost": job["estimated_cost"]}

@app.post("/api/projects/{project_id}/select/screenplay")
async def select_screenplay(project_id: str, request: SelectScreenplayRequest):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    project = projects_db[project_id]
    project["selectedScreenplay"] = request.screenplayId
    project["currentStep"] = WorkflowStep.STORYBOARD
    project["updatedAt"] = datetime.now().isoformat()
    return project

@app.post("/api/projects/{project_id}/generate/storyboard")
async def generate_storyboard(project_id: str, background_tasks: BackgroundTasks):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    project = projects_db[project_id]
    if "selectedScreenplay" not in project:
        raise HTTPException(status_code=400, detail="Screenplay not selected")
    
    job = create_job(project_id, "storyboard")
    background_tasks.add_task(run_generation_with_pipeline, job["id"], project_id, "storyboard", {"screenplayId": project["selectedScreenplay"]})
    
    return {"jobId": job["id"], "estimatedTime": job["estimated_time"], "estimatedCost": job["estimated_cost"]}

@app.post("/api/projects/{project_id}/generate/production")
async def generate_production_pack(project_id: str, background_tasks: BackgroundTasks):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    project = projects_db[project_id]
    if "storyboard" not in project:
        raise HTTPException(status_code=400, detail="Storyboard not generated")
    
    job = create_job(project_id, "production")
    background_tasks.add_task(run_generation_with_pipeline, job["id"], project_id, "production", {"storyboardId": project["storyboard"]["id"]})
    
    return {"jobId": job["id"], "estimatedTime": job["estimated_time"], "estimatedCost": job["estimated_cost"]}

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs_db[job_id]

@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs_db[job_id]
    job["status"] = "cancelled"
    return {"message": "Job cancelled"}

@app.get("/api/stream/generation/{job_id}")
async def stream_generation_progress(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    async def event_generator():
        job = jobs_db[job_id]
        while job["status"] in ["pending", "running"]:
            data = {"type": "progress", "data": {"progress": job["progress"], "step": job["step"], "message": f"Processing {job['step']}..."}}
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(1)
        
        if job["status"] == "completed":
            data = {"type": "complete", "data": {"message": "Generation completed"}}
        else:
            data = {"type": "error", "data": {"message": job.get("error", "Generation failed")}}
        yield f"data: {json.dumps(data)}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=2502)  # Different port to avoid conflict
