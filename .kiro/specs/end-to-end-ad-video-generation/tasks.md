# Implementation Plan: End-to-End Ad Video Generation

## Overview

This implementation plan extends the existing LangGraph ad storyboarding pipeline to produce complete 30-60 second advertisement videos. The implementation will be done in Python, maintaining the existing StateGraph pattern while adding new nodes for video generation, assembly, and quality control.

**CRITICAL**: All new code must follow the exact coding style and patterns from `05_movie_storyboarding.ipynb`. This includes:
- Using the same agent+tools pattern for each node
- Preserving all existing prompt templates (Rajamouli and Shankar styles)
- Maintaining the LangGraph StateGraph orchestration
- Following the same function naming conventions (e.g., `*_node` suffix)
- Using the same display/output patterns with Markdown

## Tasks

- [x] 0. Convert notebook to Python module
  - [x] 0.1 Create `ad_video_pipeline.py` from `05_movie_storyboarding.ipynb`
    - Extract all code cells from the notebook
    - Remove Colab-specific code (e.g., `display(Markdown(...))` can be replaced with `print()`)
    - Preserve all existing node functions exactly as they are
    - Preserve all prompt templates (concept_creator_prompt, screenplay_writer_prompt for both styles)
    - Keep the State TypedDict definition
    - Keep the StateGraph setup and edge definitions
    - Add proper imports at the top
    - _Requirements: 2.1, 2.2_
  
  - [x] 0.2 Test the converted module
    - Run the converted module to ensure it works
    - Verify all existing nodes execute correctly
    - Verify the graph compiles without errors
    - _Requirements: 2.1, 2.2_

- [x] 1. Set up project dependencies and environment
  - Install required Python packages: `google-genai>=0.8.0`, `ffmpeg-python>=0.2.0`, `hypothesis>=6.0.0`, `pydantic>=2.0.0`
  - Verify FFmpeg is installed on the system
  - Set up environment variables for API keys (GEMINI_API_KEY, GOOGLE_CLOUD_PROJECT)
  - Create output and temp directories
  - _Requirements: 1.1, 1.5_

- [x] 2. Extend State TypedDict with new fields
  - [x] 2.1 Define new TypedDict classes (Scene, StoryboardFrame, VideoClip, CreativeBrief)
    - Create `Scene` with fields: scene_number, duration_sec, visual_description, audio_description, text_overlay
    - Create `StoryboardFrame` with fields: scene_number, image_url, prompt, generation_timestamp
    - Create `VideoClip` with fields: scene_number, video_url, duration_sec, generation_timestamp
    - Create `CreativeBrief` with fields: theme, brand_name, target_duration_sec, aspect_ratio, platform, and optional fields
    - _Requirements: 3.4, 4.5, 5.6, 1.1_
  
  - [x] 2.2 Extend State TypedDict with new fields
    - Add fields: creative_brief, auto_select_screenplay, scenes, storyboard_frames, video_clips, final_video_url, manifest_url, qc_status, safety_status
    - Preserve existing fields: theme, concept, screenplay_1, screenplay_2, screenplay_winner, story_board, overall_status
    - Use Annotated types with operator.add for status fields
    - _Requirements: 11.1, 11.2, 11.3_
  
  - [ ]* 2.3 Write property test for State schema extension
    - **Property 14: State Schema Extension**
    - **Validates: Requirements 11.1, 11.2**

- [x] 3. Implement creative brief parser and input validation
  - [x] 3.1 Create parse_creative_brief function
    - Validate required fields: theme, brand_name, target_duration_sec, aspect_ratio, platform
    - Validate target_duration_sec is 30 or 60
    - Validate aspect_ratio is one of: "16:9", "9:16", "1:1", "4:5"
    - Set default values for optional fields
    - Return CreativeBrief object
    - _Requirements: 1.1, 1.5_
  
  - [ ]* 3.2 Write property test for input validation
    - **Property 20: Input Validation**
    - **Validates: Requirements 1.1, 1.5**
  
  - [ ]* 3.3 Write unit tests for edge cases
    - Test invalid duration (not 30 or 60)
    - Test missing required fields
    - Test invalid aspect ratio
    - _Requirements: 1.1, 1.5_

- [x] 4. Implement scene breakdown node
  - [x] 4.1 Create scene_breakdown_node function
    - Use LLM with structured output to generate scenes
    - For 30-second videos: generate 4-6 scenes
    - For 60-second videos: generate 6-10 scenes
    - Enforce JSON schema validation for each scene
    - Validate sum of scene durations equals target_duration_sec (±2 seconds)
    - Return dict with 'scenes' key
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ]* 4.2 Write property test for scene count based on duration
    - **Property 1: Scene Count Based on Duration**
    - **Validates: Requirements 1.2, 1.3, 3.2, 3.3**
  
  - [ ]* 4.3 Write property test for scene duration sum invariant
    - **Property 2: Scene Duration Sum Invariant**
    - **Validates: Requirements 3.5**
  
  - [ ]* 4.4 Write property test for scene schema compliance
    - **Property 3: Scene Schema Compliance**
    - **Validates: Requirements 3.4**

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Replace DALLE-3 with Gemini 2.5 Flash in storyboard generation
  - [x] 6.1 Create generate_frame_with_gemini function
    - Initialize Gemini client with API key
    - Call gemini-2.5-flash-image model with generateContent
    - Use scene.visual_description as prompt
    - Configure response_modalities=["image"]
    - Handle API errors and implement retry logic
    - Return image URL or path
    - _Requirements: 4.1, 4.3_
  
  - [x] 6.2 Update story_board_creation_node to use Gemini
    - Replace DALLE-3 calls with generate_frame_with_gemini
    - Generate one frame per scene
    - Store frames with metadata (scene_number, image_url, prompt, timestamp)
    - Add storyboard_frames to State
    - _Requirements: 4.1, 4.2, 4.4, 4.5_
  
  - [ ]* 6.3 Write property test for Gemini API usage
    - **Property 6: Gemini API Usage**
    - **Validates: Requirements 4.1, 4.3**
  
  - [ ]* 6.4 Write property test for artifact cardinality (frames)
    - **Property 4: Artifact Cardinality** (frames part)
    - **Validates: Requirements 4.2**
  
  - [ ]* 6.5 Write property test for artifact-scene linkage (frames)
    - **Property 5: Artifact-Scene Linkage** (frames part)
    - **Validates: Requirements 4.4**

- [x] 7. Implement video clip generation node with Veo 3.1
  - [x] 7.1 Create generate_video_with_veo function
    - Initialize Gemini client with API key
    - Call veo-3.1 model with generate_video
    - Provide prompt (visual_description + audio_description)
    - Provide reference_image (storyboard frame)
    - Set duration (max 8 seconds per clip)
    - Set aspect_ratio and resolution (1080p)
    - Implement async polling for job completion
    - Handle API errors and implement retry logic
    - Return video URL
    - _Requirements: 5.2, 5.3, 5.4_
  
  - [x] 7.2 Create video_generation_node function
    - Generate one clip per scene using generate_video_with_veo
    - For scenes > 8 seconds, split into multiple clips
    - Store clips with metadata (scene_number, video_url, duration_sec, timestamp)
    - Add video_clips to State
    - _Requirements: 5.1, 5.2, 5.5, 5.6_
  
  - [ ]* 7.3 Write property test for Veo API parameters
    - **Property 7: Veo API Parameters**
    - **Validates: Requirements 5.3**
  
  - [ ]* 7.4 Write property test for artifact cardinality (clips)
    - **Property 4: Artifact Cardinality** (clips part)
    - **Validates: Requirements 5.2**
  
  - [ ]* 7.5 Write property test for artifact-scene linkage (clips)
    - **Property 5: Artifact-Scene Linkage** (clips part)
    - **Validates: Requirements 5.5**
  
  - [ ]* 7.6 Write property test for aspect ratio preservation (clips)
    - **Property 8: Aspect Ratio Preservation** (clips part)
    - **Validates: Requirements 5.4**

- [x] 8. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement video assembly node with FFmpeg
  - [x] 9.1 Create assemble_video_with_ffmpeg function
    - Create concat file listing all video clips in scene_number order
    - Build FFmpeg command with drawtext filters for text overlays
    - Calculate start/end times for each text overlay based on scene durations
    - Add subtitle/caption generation from audio_descriptions
    - Set output format: MP4, libx264 codec, specified aspect_ratio
    - Execute FFmpeg command
    - Return path to assembled video
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [x] 9.2 Create video_assembly_node function
    - Call assemble_video_with_ffmpeg with video_clips and scenes
    - Add final_video_url to State
    - _Requirements: 6.1, 6.5_
  
  - [ ]* 9.3 Write property test for video clip ordering
    - **Property 9: Video Clip Ordering**
    - **Validates: Requirements 6.1**
  
  - [ ]* 9.4 Write property test for text overlay presence
    - **Property 10: Text Overlay Presence**
    - **Validates: Requirements 6.2**
  
  - [ ]* 9.5 Write property test for aspect ratio preservation (final video)
    - **Property 8: Aspect Ratio Preservation** (final video part)
    - **Validates: Requirements 6.4**
  
  - [ ]* 9.6 Write unit tests for FFmpeg command generation
    - Test concat file creation
    - Test drawtext filter generation
    - Test caption generation
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 10. Implement QC validation node
  - [x] 10.1 Create qc_validation_node function
    - Check video duration matches target_duration_sec (±2 seconds)
    - Verify all scenes have corresponding video clips
    - Validate aspect_ratio matches creative brief
    - Check video resolution (720p or 1080p)
    - Verify audio track exists
    - Set qc_status to "QC_PASSED" or "QC_FAILED"
    - Update overall_status with QC results
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ]* 10.2 Write property test for QC validation completeness
    - **Property 11: QC Validation Completeness**
    - **Validates: Requirements 7.1, 7.2, 7.3**
  
  - [ ]* 10.3 Write property test for QC status marking
    - **Property 12: QC Status Marking**
    - **Validates: Requirements 7.4, 7.5**
  
  - [ ]* 10.4 Write unit tests for QC edge cases
    - Test duration mismatch detection
    - Test missing clip detection
    - Test aspect ratio mismatch detection
    - _Requirements: 7.1, 7.2, 7.3_

- [x] 11. Implement manifest generation node
  - [x] 11.1 Create manifest_generation_node function
    - Build manifest dict with all required sections
    - Include complete creative brief
    - Include all generated artifacts (concept, screenplays, scenes, frames, clips, final_video)
    - Include timestamps for each processing step
    - Include model versions (Gemini 2.5 Flash, Veo 3.1)
    - Include QC status and safety checks
    - Write manifest to manifest.json file
    - Add manifest_url to State
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_
  
  - [ ]* 11.2 Write property test for manifest completeness
    - **Property 13: Manifest Completeness**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4**
  
  - [ ]* 11.3 Write unit tests for manifest structure
    - Test JSON serialization
    - Test all required fields present
    - Test timestamp format
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 12. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Implement safety validation module
  - [ ] 13.1 Create validate_safety function
    - Integrate with Google Cloud Content Safety API or similar
    - Check for: violence, hate speech, adult content, brand safety violations
    - Support text, image, and video content types
    - Return dict with 'passed' (bool) and 'violations' (List[str])
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ] 13.2 Add safety checks to existing nodes
    - Add safety validation after concept generation
    - Add safety validation after screenplay generation
    - Add safety validation after storyboard frame generation
    - Add safety validation after video clip generation
    - Update safety_status in State after each check
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [ ]* 13.3 Write property test for safety violation handling
    - **Property 19: Safety Violation Handling**
    - **Validates: Requirements 10.5**
  
  - [ ]* 13.4 Write unit tests for safety checks
    - Test with known safe content
    - Test with known unsafe content
    - Test error handling
    - _Requirements: 10.5_

- [ ] 14. Implement error handling and retry logic
  - [ ] 14.1 Create retry_with_backoff decorator
    - Implement exponential backoff (base_delay=1.0, max_delay=60.0)
    - Support max_retries=3
    - Distinguish between transient and permanent errors
    - Log all retry attempts
    - _Requirements: 12.1_
  
  - [ ] 14.2 Add error handling to all nodes
    - Wrap API calls with retry_with_backoff
    - Catch permanent errors and halt processing
    - Update overall_status with error details
    - Preserve partial results in State
    - Provide clear error messages with node name and reason
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [ ]* 14.3 Write property test for transient error retry
    - **Property 16: Transient Error Retry**
    - **Validates: Requirements 12.1**
  
  - [ ]* 14.4 Write property test for permanent error handling
    - **Property 17: Permanent Error Handling**
    - **Validates: Requirements 12.2, 12.3**
  
  - [ ]* 14.5 Write property test for partial state preservation
    - **Property 18: Partial State Preservation**
    - **Validates: Requirements 12.4**
  
  - [ ]* 14.6 Write unit tests for error scenarios
    - Test API timeout handling
    - Test rate limit handling
    - Test invalid input handling
    - Test safety violation handling
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 15. Implement auto screenplay selection
  - [ ] 15.1 Create auto_screenplay_selection_node function
    - Use LLM to evaluate both screenplays based on criteria
    - Select best screenplay automatically
    - Set screenplay_winner in State
    - _Requirements: 2.3_
  
  - [ ] 15.2 Add conditional routing for screenplay selection
    - Check auto_select_screenplay flag in State
    - Route to auto_screenplay_selection_node if enabled
    - Route to manual screenplay_evaluation_node if disabled
    - _Requirements: 2.3, 2.4_
  
  - [ ]* 15.3 Write property test for auto screenplay selection
    - **Property 23: Auto Screenplay Selection**
    - **Validates: Requirements 2.3**
  
  - [ ]* 15.4 Write unit test for manual screenplay selection
    - Test that manual node is called when auto mode disabled
    - _Requirements: 2.4_

- [ ] 16. Implement HITL checkpoints (optional)
  - [ ] 16.1 Create hitl_checkpoint_node function
    - Display current artifacts (screenplays, frames, or clips)
    - Prompt user for approval (approve/reject/regenerate)
    - Handle user input and route accordingly
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ] 16.2 Add conditional HITL checkpoints to graph
    - Add checkpoint after screenplay selection (if enabled)
    - Add checkpoint after storyboard frame generation (if enabled)
    - Add checkpoint after video clip generation (if enabled)
    - Check ENABLE_HITL_CHECKPOINTS environment variable
    - _Requirements: 9.1, 9.2, 9.3_

- [ ] 17. Wire all nodes into LangGraph StateGraph
  - [ ] 17.1 Update StateGraph with new nodes
    - Add scene_breakdown_node after screenplay selection
    - Update story_board_creation_node (already exists, just modified)
    - Add video_generation_node after storyboard creation
    - Add video_assembly_node after video generation
    - Add qc_validation_node after video assembly
    - Add manifest_generation_node after QC validation
    - _Requirements: 3.1, 5.1, 6.1_
  
  - [ ] 17.2 Add edges to connect nodes
    - Connect screenplay selection → scene_breakdown_node
    - Connect scene_breakdown_node → story_board_creation_node
    - Connect story_board_creation_node → video_generation_node
    - Connect video_generation_node → video_assembly_node
    - Connect video_assembly_node → qc_validation_node
    - Connect qc_validation_node → manifest_generation_node
    - Connect manifest_generation_node → END
    - _Requirements: 3.1, 5.1, 6.1_
  
  - [ ] 17.3 Add conditional edges for HITL checkpoints
    - Add conditional edge after screenplay selection (if HITL enabled)
    - Add conditional edge after storyboard creation (if HITL enabled)
    - Add conditional edge after video generation (if HITL enabled)
    - _Requirements: 9.1, 9.2, 9.3_
  
  - [ ]* 17.4 Write property test for state validation at transitions
    - **Property 15: State Validation at Transitions**
    - **Validates: Requirements 11.5**
  
  - [ ]* 17.5 Write property test for backward compatibility
    - **Property 22: Backward Compatibility**
    - **Validates: Requirements 2.1, 2.2**

- [ ] 18. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 19. Create end-to-end integration tests
  - [ ]* 19.1 Write integration test for 30-second video generation
    - Test complete pipeline with 30-second creative brief
    - Verify all artifacts generated correctly
    - Verify final video meets specifications
    - _Requirements: 1.2, 3.2_
  
  - [ ]* 19.2 Write integration test for 60-second video generation
    - Test complete pipeline with 60-second creative brief
    - Verify all artifacts generated correctly
    - Verify final video meets specifications
    - _Requirements: 1.3, 3.3_
  
  - [ ]* 19.3 Write integration test with optional fields
    - **Property 21: Optional Field Incorporation**
    - **Validates: Requirements 1.4**
  
  - [ ]* 19.4 Write integration test with HITL checkpoints
    - Test pipeline with HITL enabled
    - Simulate user approvals at each checkpoint
    - _Requirements: 9.1, 9.2, 9.3_
  
  - [ ]* 19.5 Write integration test with error recovery
    - Inject errors at various stages
    - Verify error handling and partial state preservation
    - _Requirements: 12.1, 12.2, 12.3, 12.4_

- [ ] 20. Create example notebook demonstrating the pipeline
  - Create Jupyter notebook with example usage
  - Show creative brief input
  - Show pipeline execution
  - Display generated artifacts (concept, screenplay, scenes, frames, clips)
  - Show final video and manifest
  - Include examples with both 30-second and 60-second videos
  - _Requirements: All_

- [ ] 21. Final checkpoint - Ensure all tests pass and documentation is complete
  - Ensure all tests pass, ask the user if questions arise.
  - Verify all requirements are implemented
  - Verify all properties are tested
  - Review code quality and documentation

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end flows
- The implementation preserves the existing LangGraph StateGraph pattern
- All new nodes follow the agent+tools pattern
- Error handling and retry logic are implemented throughout
- Safety checks are integrated at key stages
- HITL checkpoints are optional and configurable
