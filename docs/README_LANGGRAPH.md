# LangGraph Flow - Complete Guide

## Quick Summary

**LangGraph** = Flowchart + State Management + Parallel Execution

Our production pipeline uses LangGraph to orchestrate 17 nodes that generate complete ad production packs with Gemini images.

## 📚 Documentation Files

1. **`LANGGRAPH_FLOW_EXPLAINED.md`** - Conceptual overview with diagrams
2. **`LANGGRAPH_CODE_EXAMPLE.md`** - Step-by-step code walkthrough
3. **`LANGGRAPH_VISUAL_SUMMARY.txt`** - ASCII art visual flow
4. **`README_LANGGRAPH.md`** - This file (quick reference)

## 🎯 Core Concepts

### 1. State (Shared Data)
```python
class State(TypedDict):
    theme: str
    concept: str
    screenplay_1: str
    screenplay_2: str
    storyboard_frames: List[dict]  # With Gemini images!
    scene_plan: dict
    budget_estimate: dict
    # ... more fields
```

### 2. Nodes (Functions)
```python
def ad_concept_creation_node(state: State) -> dict:
    # Read from state
    theme = state.get("theme")
    
    # Do work
    concept = call_tamus_api(f"Create concept for {theme}")
    
    # Return updates
    return {"concept": concept}
```

### 3. Graph (Workflow)
```python
workflow = StateGraph(State)
workflow.add_node("concept", ad_concept_creation_node)
workflow.add_node("screenplay_1", screen_play_creation_node_1)
workflow.add_edge("concept", "screenplay_1")  # concept → screenplay_1
pipeline = workflow.compile()
```

### 4. Execution
```python
initial_state = {"theme": "Sustainable tech", ...}
final_state = pipeline.invoke(initial_state)
print(final_state["concept"])
print(final_state["storyboard_frames"])  # With Gemini images!
```

## 🔄 Flow Patterns

### Sequential
```
A → B → C
```
```python
workflow.add_edge("A", "B")
workflow.add_edge("B", "C")
```

### Parallel (Fan-Out)
```
    ┌→ B
A ──┼→ C
    └→ D
```
```python
workflow.add_edge("A", "B")
workflow.add_edge("A", "C")
workflow.add_edge("A", "D")
```

### Fan-In (Wait for All)
```
B ─┐
C ─┼→ E
D ─┘
```
```python
workflow.add_edge("B", "E")
workflow.add_edge("C", "E")
workflow.add_edge("D", "E")
```

### HITL Gate (Human Approval)
```
A → [⏸️ Wait for user] → B
```
```python
def approval_gate(state):
    approval = input("Approve? (yes/no): ")
    return {"approved": approval == "yes"}
```

## 📊 Our Pipeline

### Phase 1: Creative Chain
```
START
  ↓
Concept (TAMUS)
  ↓
  ├→ Screenplay 1 (Rajamouli) ─┐
  └→ Screenplay 2 (Shankar)  ──┤ ⚡ Parallel
                               ↓
                    User Selects Winner (HITL)
                               ↓
                    Storyboard + Gemini Images 🎨
```

### Phase 2: Production Planning
```
Scene Breakdown
  ↓
Scene Approval (HITL)
  ↓
  ├→ Location Planning  ┐
  ├→ Budget Estimation  │
  ├→ Schedule Planning  │
  ├→ Casting            │ ⚡ All 8 run in parallel
  ├→ Props & Wardrobe   │
  ├→ Crew & Gear        │
  ├→ Legal Clearances   │
  └→ Risk & Safety      ┘
  ↓
Budget/Schedule Approval (HITL)
  ↓
Client Review Pack
  ↓
END
```

## 🎨 Gemini Integration

```python
def story_board_creation_node(state: State) -> dict:
    # Generate descriptions with TAMUS
    frames = generate_frame_descriptions(state["screenplay_winner"])
    
    # Generate images with Gemini 2.5 Flash
    import google.genai as genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    storyboard_frames = []
    for frame in frames:
        response = client.models.generate_images(
            model="gemini-2.5-flash",
            prompt=frame["description"],
            config={"aspect_ratio": "16:9"}
        )
        
        storyboard_frames.append({
            "frame_number": frame["frame_number"],
            "description": frame["description"],
            "image_url": response.generated_images[0].image.url,  # ← Gemini!
            "duration_sec": frame["duration_sec"]
        })
    
    return {"storyboard_frames": storyboard_frames}
```

## 🌐 Web Version

For the web UI, we remove HITL gates:

```python
# Full pipeline (command-line)
def screenplay_evaluation_node(state):
    choice = input("Pick 1 or 2: ")  # ← HITL gate
    return {"screenplay_winner": state[f"screenplay_{choice}"]}

# Web pipeline (auto-approve)
def screenplay_evaluation_node(state):
    return {"screenplay_winner": state["screenplay_1"]}  # ← Auto-select
```

## 📈 Benefits

| Feature | Without LangGraph | With LangGraph |
|---------|-------------------|----------------|
| **Orchestration** | Manual | ✅ Automatic |
| **State Passing** | Manual | ✅ Automatic |
| **Parallel Execution** | Complex | ✅ Simple |
| **HITL Gates** | Custom code | ✅ Built-in |
| **Debugging** | Difficult | ✅ Easy |
| **Visualization** | None | ✅ Graph view |

## 🚀 Quick Start

### 1. Run Full Pipeline
```bash
python example_pipeline_usage.py
```

### 2. Run Web Pipeline
```bash
python test_backend_integration.py
```

### 3. Integrate with Backend
```python
from backend.pipeline_integration import get_pipeline_runner

runner = get_pipeline_runner()
result = await runner.generate_concept(project_id, brief)
```

## 📝 Key Files

- **`ad_production_pipeline.py`** - Full pipeline with HITL gates
- **`ad_production_pipeline_web.py`** - Web version (no HITL)
- **`backend/pipeline_integration.py`** - Backend integration layer
- **`models/*.py`** - Data models (TypedDicts)
- **`tamus_wrapper.py`** - TAMUS API client

## 🎯 Summary

**LangGraph makes it easy to:**
- ✅ Build complex workflows as graphs
- ✅ Manage state automatically
- ✅ Run nodes in parallel
- ✅ Add human approval gates
- ✅ Debug and visualize flow

**Our pipeline:**
- 17 nodes
- 2 HITL gates
- 8 parallel production nodes
- Gemini 2.5 Flash for images
- Complete production packs

All orchestrated cleanly with LangGraph! 🚀

## 📖 Learn More

- Read `LANGGRAPH_FLOW_EXPLAINED.md` for detailed concepts
- Read `LANGGRAPH_CODE_EXAMPLE.md` for code walkthrough
- View `LANGGRAPH_VISUAL_SUMMARY.txt` for visual flow
- Check LangGraph docs: https://langchain-ai.github.io/langgraph/
