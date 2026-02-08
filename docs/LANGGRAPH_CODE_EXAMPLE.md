# LangGraph Code Example - Step by Step

## Complete Working Example

Let me show you exactly how our pipeline works with real code:

### Step 1: Define State

```python
from typing import TypedDict, List, Annotated
import operator

class State(TypedDict):
    """Shared data structure that flows through pipeline"""
    
    # Input
    theme: str
    creative_brief: dict
    
    # Generated content
    concept: str
    screenplay_1: str
    screenplay_2: str
    screenplay_winner: str
    storyboard_frames: List[dict]
    
    # Status tracking
    overall_status: Annotated[str, operator.add]  # Accumulates messages
```

**What this means:**
- Every node can read/write to this state
- `Annotated[str, operator.add]` means status messages get concatenated
- State is passed automatically between nodes

### Step 2: Create Nodes (Functions)

```python
def ad_concept_creation_node(state: State) -> dict:
    """
    Node 1: Generate concept
    
    Input from state:
        - theme: "Sustainable technology"
        - creative_brief: {"brand_name": "EcoPhone", ...}
    
    Output (updates to state):
        - concept: "Generated concept text..."
        - overall_status: "Concept created. "
    """
    
    # 1. Read from state
    theme = state.get("theme", "")
    brand = state.get("creative_brief", {}).get("brand_name", "")
    
    # 2. Do work (call API)
    prompt = f"Create ad concept for {brand} about {theme}"
    concept = call_tamus_api(prompt)
    
    # 3. Return updates (will be merged into state)
    return {
        "concept": concept,
        "overall_status": "Concept created. "
    }


def screen_play_creation_node_1(state: State) -> dict:
    """
    Node 2A: Generate Rajamouli-style screenplay
    
    Input from state:
        - concept: "Generated concept text..."
    
    Output:
        - screenplay_1: "SCENE 1: Epic opening..."
    """
    
    concept = state.get("concept", "")
    
    prompt = f"Write Rajamouli-style screenplay for: {concept}"
    screenplay = call_tamus_api(prompt)
    
    return {
        "screenplay_1": screenplay,
        "overall_status": "Rajamouli screenplay created. "
    }


def screen_play_creation_node_2(state: State) -> dict:
    """
    Node 2B: Generate Shankar-style screenplay
    
    Runs in PARALLEL with node 2A
    """
    
    concept = state.get("concept", "")
    
    prompt = f"Write Shankar-style screenplay for: {concept}"
    screenplay = call_tamus_api(prompt)
    
    return {
        "screenplay_2": screenplay,
        "overall_status": "Shankar screenplay created. "
    }


def screenplay_evaluation_node(state: State) -> dict:
    """
    Node 3: User selects winning screenplay (HITL gate)
    
    Input from state:
        - screenplay_1: "..."
        - screenplay_2: "..."
    
    Output:
        - screenplay_winner: (one of the above)
    """
    
    print("Screenplay 1:", state.get("screenplay_1", "")[:200])
    print("Screenplay 2:", state.get("screenplay_2", "")[:200])
    
    # HITL: Wait for user input
    choice = input("Pick 1 or 2: ")
    
    if choice == "1":
        winner = state.get("screenplay_1", "")
    else:
        winner = state.get("screenplay_2", "")
    
    return {
        "screenplay_winner": winner,
        "overall_status": "Screenplay selected. "
    }


def story_board_creation_node(state: State) -> dict:
    """
    Node 4: Generate storyboard with Gemini images
    
    Input from state:
        - screenplay_winner: "..."
    
    Output:
        - storyboard_frames: [
            {"frame_number": 1, "image_url": "...", ...},
            ...
          ]
    """
    
    screenplay = state.get("screenplay_winner", "")
    
    # Generate frame descriptions
    frames_json = call_tamus_api(f"Create storyboard for: {screenplay}")
    frames = json.loads(frames_json)
    
    # Generate images with Gemini
    import google.genai as genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    storyboard_frames = []
    for frame in frames:
        # Generate image
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
    
    return {
        "storyboard_frames": storyboard_frames,
        "overall_status": "Storyboard created. "
    }
```

### Step 3: Build the Graph

```python
from langgraph.graph import StateGraph

def create_production_pipeline():
    """Build the LangGraph workflow"""
    
    # 1. Create empty graph with State type
    workflow = StateGraph(State)
    
    # 2. Add nodes (give each a name and function)
    workflow.add_node("concept", ad_concept_creation_node)
    workflow.add_node("screenplay_1", screen_play_creation_node_1)
    workflow.add_node("screenplay_2", screen_play_creation_node_2)
    workflow.add_node("evaluation", screenplay_evaluation_node)
    workflow.add_node("storyboard", story_board_creation_node)
    
    # 3. Define flow (edges)
    workflow.set_entry_point("concept")  # Start here
    
    # Sequential: concept → both screenplays
    workflow.add_edge("concept", "screenplay_1")
    workflow.add_edge("concept", "screenplay_2")
    
    # Both screenplays → evaluation
    workflow.add_edge("screenplay_1", "evaluation")
    workflow.add_edge("screenplay_2", "evaluation")
    
    # Evaluation → storyboard
    workflow.add_edge("evaluation", "storyboard")
    
    workflow.set_finish_point("storyboard")  # End here
    
    # 4. Compile into executable pipeline
    return workflow.compile()
```

**Visual representation:**
```
START
  ↓
[concept]
  ↓
  ├→ [screenplay_1] ─┐
  └→ [screenplay_2] ─┤
                     ↓
              [evaluation]
                     ↓
              [storyboard]
                     ↓
                    END
```

### Step 4: Execute the Pipeline

```python
# Create pipeline
pipeline = create_production_pipeline()

# Define initial state
initial_state = {
    "theme": "Sustainable technology for a better tomorrow",
    "creative_brief": {
        "brand_name": "EcoPhone",
        "target_duration_sec": 30,
        "aspect_ratio": "16:9"
    },
    "overall_status": ""
}

# Run pipeline (this executes all nodes in order)
print("Starting pipeline...")
final_state = pipeline.invoke(initial_state)

# Access results
print("\n=== RESULTS ===")
print("Concept:", final_state["concept"][:200])
print("Screenplay 1:", final_state["screenplay_1"][:200])
print("Screenplay 2:", final_state["screenplay_2"][:200])
print("Winner:", final_state["screenplay_winner"][:200])
print("Storyboard frames:", len(final_state["storyboard_frames"]))

for frame in final_state["storyboard_frames"]:
    print(f"  Frame {frame['frame_number']}: {frame['image_url']}")

print("\nStatus:", final_state["overall_status"])
```

**Output:**
```
Starting pipeline...
------ENTERING: CONCEPT CREATION NODE------
Generated Concept: Innovation meets sustainability...
------ENTERING: SCREENPLAY CREATION NODE 1 (RAJAMOULI STYLE)------
Generated Rajamouli Screenplay: SCENE 1: Epic opening...
------ENTERING: SCREENPLAY CREATION NODE 2 (SHANKAR STYLE)------
Generated Shankar Screenplay: SCENE 1: Futuristic tech...
------ENTERING: SCREENPLAY EVALUATION NODE------
Screenplay 1: SCENE 1: Epic opening with sweeping camera...
Screenplay 2: SCENE 1: Futuristic tech lab with holographic...
Pick 1 or 2: 1
Selected: Rajamouli style screenplay
------ENTERING: STORY BOARD CREATION NODE------
Generating 5 storyboard images with Gemini 2.5 Flash...
  ✓ Generated frame 1
  ✓ Generated frame 2
  ✓ Generated frame 3
  ✓ Generated frame 4
  ✓ Generated frame 5

=== RESULTS ===
Concept: Innovation meets sustainability in this compelling...
Screenplay 1: SCENE 1: Epic opening with sweeping camera...
Screenplay 2: SCENE 1: Futuristic tech lab with holographic...
Winner: SCENE 1: Epic opening with sweeping camera...
Storyboard frames: 5
  Frame 1: https://generativelanguage.googleapis.com/...
  Frame 2: https://generativelanguage.googleapis.com/...
  Frame 3: https://generativelanguage.googleapis.com/...
  Frame 4: https://generativelanguage.googleapis.com/...
  Frame 5: https://generativelanguage.googleapis.com/...

Status: Concept created. Rajamouli screenplay created. Shankar screenplay created. Screenplay selected. Storyboard created.
```

## How State Flows

Let's trace state through each node:

```python
# Initial state
{
    "theme": "Sustainable technology",
    "creative_brief": {"brand_name": "EcoPhone", ...},
    "overall_status": ""
}

# ↓ After concept node

{
    "theme": "Sustainable technology",
    "creative_brief": {"brand_name": "EcoPhone", ...},
    "concept": "Innovation meets sustainability...",  # ← ADDED
    "overall_status": "Concept created. "             # ← ADDED
}

# ↓ After screenplay_1 node (parallel)

{
    ...
    "concept": "Innovation meets sustainability...",
    "screenplay_1": "SCENE 1: Epic opening...",       # ← ADDED
    "overall_status": "Concept created. Rajamouli screenplay created. "
}

# ↓ After screenplay_2 node (parallel, runs at same time as screenplay_1)

{
    ...
    "screenplay_1": "SCENE 1: Epic opening...",
    "screenplay_2": "SCENE 1: Futuristic tech...",    # ← ADDED
    "overall_status": "Concept created. Rajamouli screenplay created. Shankar screenplay created. "
}

# ↓ After evaluation node (waits for user input)

{
    ...
    "screenplay_1": "SCENE 1: Epic opening...",
    "screenplay_2": "SCENE 1: Futuristic tech...",
    "screenplay_winner": "SCENE 1: Epic opening...",  # ← ADDED (user picked 1)
    "overall_status": "... Screenplay selected. "
}

# ↓ After storyboard node (generates Gemini images)

{
    ...
    "screenplay_winner": "SCENE 1: Epic opening...",
    "storyboard_frames": [                            # ← ADDED
        {
            "frame_number": 1,
            "description": "Epic hero shot",
            "image_url": "https://gemini.../img1.jpg",  # ← Gemini image!
            "duration_sec": 5.0
        },
        {
            "frame_number": 2,
            "description": "Product reveal",
            "image_url": "https://gemini.../img2.jpg",  # ← Gemini image!
            "duration_sec": 5.0
        },
        ...
    ],
    "overall_status": "... Storyboard created. "
}
```

## Parallel Execution Example

```python
# When you have this:
workflow.add_edge("concept", "screenplay_1")
workflow.add_edge("concept", "screenplay_2")

# LangGraph does this:
def execute():
    state = run_node("concept", state)
    
    # Run both in parallel (using threads)
    with ThreadPoolExecutor() as executor:
        future1 = executor.submit(run_node, "screenplay_1", state)
        future2 = executor.submit(run_node, "screenplay_2", state)
        
        result1 = future1.result()  # Wait for screenplay_1
        result2 = future2.result()  # Wait for screenplay_2
        
        # Merge both results into state
        state.update(result1)
        state.update(result2)
    
    # Continue to next node
    state = run_node("evaluation", state)
```

## HITL Gate Example

```python
def scene_plan_approval_gate(state: State) -> dict:
    """
    HITL Gate: Pipeline pauses here until user responds
    """
    
    # Display info
    scene_plan = state.get("scene_plan", {})
    print(f"Total Scenes: {len(scene_plan.get('scenes', []))}")
    print(f"Total Shots: {len(scene_plan.get('shots', []))}")
    
    # Wait for user input (pipeline is BLOCKED here)
    approval = input("Approve scene plan? (yes/no): ")
    
    if approval == "yes":
        return {"overall_status": "Scene plan approved. "}
    else:
        # Could trigger regeneration here
        return {"overall_status": "Scene plan rejected. "}
```

**Timeline:**
```
[concept] → [screenplay_1] → [screenplay_2] → [evaluation]
                                                    ↓
                                            ⏸️  PAUSED (waiting for user)
                                                    ↓
                                            User types "1"
                                                    ↓
                                            ▶️  RESUMED
                                                    ↓
                                            [storyboard]
```

## Web Version (No HITL)

For the web UI, we remove HITL gates:

```python
def screenplay_evaluation_node(state: State) -> dict:
    """
    Web version: Auto-select instead of waiting for user
    """
    
    # No input() call - just auto-select
    screenplay_winner = state.get("screenplay_1", "")
    
    return {
        "screenplay_winner": screenplay_winner,
        "overall_status": "Screenplay auto-selected. "
    }
```

## Summary

**LangGraph makes it easy to:**

1. ✅ **Define workflow as a graph** (visual, easy to understand)
2. ✅ **Manage state automatically** (no manual passing)
3. ✅ **Run nodes in parallel** (faster execution)
4. ✅ **Add HITL gates** (pause for human input)
5. ✅ **Debug easily** (inspect state at any point)

**Our pipeline:**
- 17 nodes
- Sequential + parallel execution
- HITL gates for approval
- Gemini 2.5 Flash for images
- Complete production planning

All orchestrated cleanly with LangGraph! 🚀
