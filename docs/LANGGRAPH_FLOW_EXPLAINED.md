# LangGraph Flow Explained

## What is LangGraph?

**LangGraph** is a framework for building **stateful, multi-agent workflows** as graphs. Think of it as a flowchart where:
- **Nodes** = Functions that do work (generate concept, create screenplay, etc.)
- **Edges** = Connections that control flow (what happens next)
- **State** = Shared data that flows through the pipeline

## Our Production Pipeline Flow

### Visual Flow Diagram

```
START
  ↓
┌─────────────────────────────────────────────────────────────┐
│ 1. CONCEPT GENERATION                                        │
│    Input: Theme, Brand                                       │
│    Output: Concept description                               │
└────────────────────┬────────────────────────────────────────┘
                     ↓
         ┌───────────┴───────────┐
         ↓                       ↓
┌────────────────────┐  ┌────────────────────┐
│ 2A. SCREENPLAY     │  │ 2B. SCREENPLAY     │
│     (Rajamouli)    │  │     (Shankar)      │
│  EPIC, GRAND SCALE │  │  HIGH-TECH, FUTURE │
└────────┬───────────┘  └────────┬───────────┘
         │                       │
         └───────────┬───────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. SCREENPLAY SELECTION (HITL Gate)                          │
│    User picks: Rajamouli OR Shankar                          │
│    Output: screenplay_winner                                  │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. STORYBOARD GENERATION                                     │
│    - Generate frame descriptions (TAMUS)                     │
│    - Generate images (Gemini 2.5 Flash)                      │
│    Output: storyboard_frames with images                     │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. SCENE BREAKDOWN                                           │
│    Convert storyboard → structured scene plan                │
│    Output: scenes + shots (JSON)                             │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. SCENE PLAN APPROVAL (HITL Gate)                           │
│    User reviews scene plan                                    │
│    Approve → Continue | Reject → Regenerate                   │
└────────────────────┬────────────────────────────────────────┘
                     ↓ (if approved)
         ┌───────────┴───────────┐
         ↓           ↓           ↓
    ┌────────┐  ┌────────┐  ┌────────┐
    │Location│  │ Budget │  │Schedule│  ... (8 parallel nodes)
    │Planning│  │Estimate│  │Planning│
    └────┬───┘  └────┬───┘  └────┬───┘
         │           │           │
         └───────────┴───────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. BUDGET/SCHEDULE APPROVAL (HITL Gate)                      │
│    User reviews budget & schedule                             │
│    Approve → Continue | Reject → Regenerate                   │
└────────────────────┬────────────────────────────────────────┘
                     ↓ (if approved)
┌─────────────────────────────────────────────────────────────┐
│ 8. CLIENT REVIEW PACK                                        │
│    Generate final markdown document                           │
│    Output: production_pack.md                                 │
└────────────────────┬────────────────────────────────────────┘
                     ↓
                    END
```

## Code Breakdown

### 1. Define State (Shared Data)

```python
class State(TypedDict):
    """Data that flows through the entire pipeline"""
    
    # Creative chain
    theme: str                          # Input: "Sustainable technology"
    concept: str                        # Generated concept
    screenplay_1: str                   # Rajamouli screenplay
    screenplay_2: str                   # Shankar screenplay
    screenplay_winner: str              # Selected screenplay
    story_board: str                    # Storyboard text
    storyboard_frames: List[...]        # Frames with Gemini images
    
    # Production planning
    scene_plan: ScenePlan              # Structured scenes + shots
    budget_estimate: BudgetEstimate    # Budget breakdown
    schedule_plan: SchedulePlan        # Shoot schedule
    # ... more fields
```

**Key Point**: State is like a shared dictionary that every node can read from and write to.

### 2. Define Nodes (Functions)

Each node is a Python function that:
- Takes `state` as input
- Does some work (call API, process data, etc.)
- Returns a dict with updates to state

```python
def ad_concept_creation_node(state: State) -> Dict:
    """Node 1: Generate concept"""
    
    # Read from state
    theme = state.get("theme", "")
    brand = state.get("creative_brief", {}).get("brand_name", "")
    
    # Do work (call TAMUS API)
    prompt = f"Create concept for {brand} about {theme}"
    concept = call_tamus_api(prompt)
    
    # Return updates to state
    return {
        "concept": concept,
        "overall_status": "Concept created. "
    }
```

### 3. Create Graph

```python
def create_production_pipeline():
    """Build the LangGraph workflow"""
    
    # Create empty graph
    workflow = StateGraph(State)
    
    # Add nodes (functions)
    workflow.add_node("concept", ad_concept_creation_node)
    workflow.add_node("screenplay_1", screen_play_creation_node_1)
    workflow.add_node("screenplay_2", screen_play_creation_node_2)
    workflow.add_node("evaluation", screenplay_evaluation_node)
    workflow.add_node("storyboard", story_board_creation_node)
    # ... more nodes
    
    # Define flow (edges)
    workflow.set_entry_point("concept")  # Start here
    
    workflow.add_edge("concept", "screenplay_1")  # concept → screenplay_1
    workflow.add_edge("concept", "screenplay_2")  # concept → screenplay_2
    workflow.add_edge("screenplay_1", "evaluation")
    workflow.add_edge("screenplay_2", "evaluation")
    workflow.add_edge("evaluation", "storyboard")
    # ... more edges
    
    workflow.set_finish_point("client_review_pack")  # End here
    
    # Compile into executable pipeline
    return workflow.compile()
```

### 4. Execute Pipeline

```python
# Create pipeline
pipeline = create_production_pipeline()

# Initial state
initial_state = {
    "theme": "Sustainable technology",
    "creative_brief": {
        "brand_name": "EcoPhone",
        "target_duration_sec": 30,
        "aspect_ratio": "16:9"
    },
    "overall_status": ""
}

# Run pipeline (executes all nodes in order)
final_state = pipeline.invoke(initial_state)

# Access results
print(final_state["concept"])
print(final_state["screenplay_winner"])
print(final_state["storyboard_frames"])
```

## Key Concepts

### 1. Sequential Execution

```python
workflow.add_edge("A", "B")  # A runs, then B runs
```

```
Node A → Node B
```

### 2. Parallel Execution (Fan-Out)

```python
workflow.add_edge("A", "B")
workflow.add_edge("A", "C")
workflow.add_edge("A", "D")
```

```
        ┌→ Node B
Node A ─┼→ Node C
        └→ Node D
```

All three nodes (B, C, D) run **at the same time** after A completes.

### 3. Fan-In (Wait for All)

```python
workflow.add_edge("B", "E")
workflow.add_edge("C", "E")
workflow.add_edge("D", "E")
```

```
Node B ─┐
Node C ─┼→ Node E
Node D ─┘
```

Node E waits until **all** of B, C, D complete before running.

### 4. HITL Gates (Human-in-the-Loop)

```python
def scene_plan_approval_gate(state: State) -> Dict:
    """Node that waits for human input"""
    
    # Display info to user
    print("Scene Plan:")
    print(state["scene_plan"])
    
    # Wait for user input
    approval = input("Approve? (yes/no): ")
    
    if approval == "yes":
        return {"overall_status": "Approved. "}
    else:
        return {"overall_status": "Rejected. "}
```

Pipeline **pauses** at this node until user responds.

## Our Pipeline in Detail

### Phase 1: Creative Chain

```python
# Sequential flow
START
  ↓
concept_node          # Generate concept
  ↓
  ├→ screenplay_1     # Rajamouli (parallel)
  └→ screenplay_2     # Shankar (parallel)
  ↓
evaluation_node       # User picks winner (HITL)
  ↓
storyboard_node       # Generate frames + Gemini images
```

**Code:**
```python
workflow.add_edge("concept", "screenplay_1")
workflow.add_edge("concept", "screenplay_2")
workflow.add_edge("screenplay_1", "evaluation")
workflow.add_edge("screenplay_2", "evaluation")
workflow.add_edge("evaluation", "storyboard")
```

### Phase 2: Production Planning

```python
storyboard_node
  ↓
scene_breakdown_node
  ↓
scene_approval_gate (HITL)
  ↓
  ├→ location_planning    ┐
  ├→ budgeting            │
  ├→ scheduling           │ All run in parallel
  ├→ casting              │ (8 nodes)
  ├→ props_wardrobe       │
  ├→ crew_gear            │
  ├→ legal_clearance      │
  └→ risk_safety          ┘
  ↓
budget_schedule_approval (HITL)
  ↓
client_review_pack_node
  ↓
END
```

**Code:**
```python
# Fan-out to 8 parallel nodes
workflow.add_edge("scene_approval", "location_planning")
workflow.add_edge("scene_approval", "budgeting")
workflow.add_edge("scene_approval", "scheduling")
workflow.add_edge("scene_approval", "casting")
workflow.add_edge("scene_approval", "props_wardrobe")
workflow.add_edge("scene_approval", "crew_gear")
workflow.add_edge("scene_approval", "legal_clearance")
workflow.add_edge("scene_approval", "risk_safety")

# Fan-in to approval gate
workflow.add_edge("location_planning", "budget_approval")
workflow.add_edge("budgeting", "budget_approval")
workflow.add_edge("scheduling", "budget_approval")
# ... all 8 nodes connect to budget_approval
```

## State Flow Example

Let's trace how state changes through the pipeline:

```python
# Initial state
state = {
    "theme": "Sustainable tech",
    "creative_brief": {...},
    "overall_status": ""
}

# After concept_node
state = {
    "theme": "Sustainable tech",
    "creative_brief": {...},
    "concept": "Innovation meets sustainability...",  # ← Added
    "overall_status": "Concept created. "             # ← Added
}

# After screenplay_1 and screenplay_2 (parallel)
state = {
    "theme": "Sustainable tech",
    "creative_brief": {...},
    "concept": "Innovation meets sustainability...",
    "screenplay_1": "SCENE 1: Epic opening...",       # ← Added
    "screenplay_2": "SCENE 1: Futuristic tech...",    # ← Added
    "overall_status": "Concept created. Screenplays created. "
}

# After evaluation_node (user picks screenplay 1)
state = {
    ...
    "screenplay_winner": "SCENE 1: Epic opening...",  # ← Added
    "overall_status": "... Screenplay selected. "
}

# After storyboard_node (with Gemini images)
state = {
    ...
    "story_board": "Frame 1: Hero shot...",
    "storyboard_frames": [                            # ← Added
        {
            "frame_number": 1,
            "description": "Hero shot of phone",
            "image_url": "https://gemini.../image1.jpg",  # ← Gemini!
            "duration_sec": 5.0
        },
        ...
    ],
    "overall_status": "... Storyboard created. "
}

# After all 8 parallel production nodes
state = {
    ...
    "scene_plan": {...},           # ← Added
    "budget_estimate": {...},      # ← Added
    "schedule_plan": {...},        # ← Added
    "locations_plan": {...},       # ← Added
    "crew_gear_package": {...},   # ← Added
    "legal_clearance_report": {...},  # ← Added
    "risk_register": {...},        # ← Added
    "casting_suggestions": {...},  # ← Added
    "props_wardrobe_list": {...},  # ← Added
}

# Final state
state = {
    ... (all above fields)
    "production_pack": "output/production_pack.md"  # ← Final output
}
```

## Why LangGraph?

### Benefits

1. **Visual Flow**: Easy to understand the pipeline as a graph
2. **State Management**: Automatic state passing between nodes
3. **Parallel Execution**: Run multiple nodes simultaneously
4. **HITL Support**: Easy to add human approval gates
5. **Debugging**: Can inspect state at any point
6. **Modularity**: Each node is independent and testable

### Comparison

**Without LangGraph (Manual):**
```python
# Manual orchestration - messy!
concept = generate_concept(theme)
screenplay_1 = generate_screenplay_1(concept)
screenplay_2 = generate_screenplay_2(concept)
winner = user_select(screenplay_1, screenplay_2)
storyboard = generate_storyboard(winner)
# ... lots of manual state passing
```

**With LangGraph:**
```python
# Clean and declarative
pipeline = create_production_pipeline()
final_state = pipeline.invoke(initial_state)
# LangGraph handles all the orchestration!
```

## Web Version Differences

### Full Pipeline (`ad_production_pipeline.py`)
- ✅ Has HITL gates (command-line prompts)
- ✅ User approves scene plan
- ✅ User approves budget/schedule
- ✅ User selects screenplay

### Web Pipeline (`ad_production_pipeline_web.py`)
- ❌ No HITL gates (auto-approves)
- ✅ Auto-selects screenplay 1
- ✅ Auto-approves scene plan
- ✅ Auto-approves budget/schedule
- ✅ Same quality output
- ✅ Same Gemini images

## Summary

**LangGraph = Flowchart + State Management**

```
Nodes (Functions) + Edges (Flow) + State (Data) = Pipeline
```

Our pipeline:
1. **17 nodes** (concept, screenplays, storyboard, scene breakdown, 8 production nodes, approval gates, review pack)
2. **Sequential + Parallel** execution (creative chain is sequential, production planning is parallel)
3. **HITL gates** for human approval (or auto-approve for web)
4. **Shared state** that accumulates data as it flows through

The result: A clean, maintainable, visual workflow that generates complete production packs with Gemini images! 🚀
