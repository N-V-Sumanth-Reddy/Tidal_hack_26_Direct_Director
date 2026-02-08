"""
Example: How to use the Ad Production Pipeline

This script demonstrates how to run the complete ad production pipeline
from creative brief to production pack generation.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ad_production_pipeline import create_production_pipeline


def main():
    """Run the ad production pipeline with an example creative brief"""
    
    print("="*70)
    print("Ad Production Pipeline - Example Usage")
    print("="*70)
    
    # Check environment variables
    print("\n1. Checking environment variables...")
    tamus_key = os.getenv("TAMUS_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not tamus_key:
        print("   ✗ TAMUS_API_KEY not set")
        print("   Please set TAMUS_API_KEY in your .env file")
        return
    else:
        print("   ✓ TAMUS_API_KEY is set")
    
    if not gemini_key:
        print("   ⚠ GEMINI_API_KEY not set (needed for storyboard images)")
    else:
        print("   ✓ GEMINI_API_KEY is set")
    
    # Create pipeline
    print("\n2. Creating production pipeline...")
    try:
        production_graph = create_production_pipeline()
        print("   ✓ Pipeline created successfully")
    except Exception as e:
        print(f"   ✗ Failed to create pipeline: {e}")
        return
    
    # Define creative brief
    print("\n3. Defining creative brief...")
    creative_brief = {
        "brand_name": "EcoPhone",
        "theme": "Sustainable technology for a better tomorrow",
        "target_duration_sec": 30,
        "aspect_ratio": "16:9"
    }
    
    print(f"   Brand: {creative_brief['brand_name']}")
    print(f"   Theme: {creative_brief['theme']}")
    print(f"   Duration: {creative_brief['target_duration_sec']}s")
    print(f"   Aspect Ratio: {creative_brief['aspect_ratio']}")
    
    # Create initial state
    print("\n4. Preparing initial state...")
    initial_state = {
        "theme": creative_brief["theme"],
        "creative_brief": creative_brief,
        "overall_status": ""
    }
    print("   ✓ Initial state prepared")
    
    # Run pipeline
    print("\n5. Running production pipeline...")
    print("   This will take several minutes as it generates:")
    print("   - Concept")
    print("   - Two screenplay variants (Rajamouli & Shankar styles)")
    print("   - Storyboard")
    print("   - Scene breakdown")
    print("   - 8 parallel production planning artifacts")
    print("   - Final production pack")
    print("\n" + "="*70)
    
    try:
        final_state = production_graph.invoke(initial_state)
        
        print("\n" + "="*70)
        print("✓ PIPELINE COMPLETE!")
        print("="*70)
        
        # Display results
        print("\nGenerated Artifacts:")
        print(f"  - Concept: {len(final_state.get('concept', ''))} characters")
        print(f"  - Screenplay 1 (Rajamouli): {len(final_state.get('screenplay_1', ''))} characters")
        print(f"  - Screenplay 2 (Shankar): {len(final_state.get('screenplay_2', ''))} characters")
        print(f"  - Winning Screenplay: {len(final_state.get('screenplay_winner', ''))} characters")
        print(f"  - Storyboard: {len(final_state.get('story_board', ''))} characters")
        
        scene_plan = final_state.get('scene_plan', {})
        if scene_plan:
            print(f"  - Scene Plan: {len(scene_plan.get('scenes', []))} scenes, {len(scene_plan.get('shots', []))} shots")
        
        budget = final_state.get('budget_estimate', {})
        if budget:
            print(f"  - Budget: ${budget.get('total_min', 0):,.0f} - ${budget.get('total_max', 0):,.0f}")
        
        schedule = final_state.get('schedule_plan', {})
        if schedule:
            print(f"  - Schedule: {schedule.get('total_shoot_days', 0)} shoot days")
        
        production_pack = final_state.get('production_pack', '')
        if production_pack:
            print(f"  - Production Pack: {production_pack}")
        
        print(f"\nOverall Status: {final_state.get('overall_status', '')}")
        
    except KeyboardInterrupt:
        print("\n\n✗ Pipeline interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
