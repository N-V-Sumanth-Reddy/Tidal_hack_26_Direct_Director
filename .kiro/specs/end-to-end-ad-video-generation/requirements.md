# Requirements Document: End-to-End Ad Video Generation

## Introduction

This feature extends the existing LangGraph-based ad storyboarding pipeline to produce complete 30-60 second advertisement videos. The system will generate concept, screenplay, storyboard frames using Gemini 2.5 Flash (replacing DALLE-3), video clips using Veo 3.1, and assemble them into a final MP4 with text overlays and captions. The system maintains the existing LangGraph StateGraph orchestration pattern while adding new nodes for video generation, assembly, and quality control.

## Glossary

- **System**: The end-to-end ad video generation pipeline
- **Creative_Brief**: Input specification containing theme, brand_name, target_duration_sec, aspect_ratio, platform, and other parameters
- **Concept**: High-level advertisement idea generated from the creative brief
- **Screenplay**: Detailed narrative script for the advertisement
- **Scene**: Individual segment of the advertisement with specific duration and visual description
- **Storyboard_Frame**: Static image representing a key moment in a scene
- **Video_Clip**: Generated video segment for a scene using Veo 3.1
- **Manifest**: JSON document containing complete lineage and metadata for the generated video
- **QC_Node**: Quality control validation node
- **HITL_Checkpoint**: Human-in-the-loop checkpoint for manual review
- **LangGraph**: Orchestration framework using StateGraph pattern
- **State**: TypedDict containing all pipeline data (theme, concept, screenplay, scenes, frames, clips, etc.)
- **Node**: Processing function in the LangGraph workflow
- **Gemini_2.5_Flash**: Google's image generation model replacing DALLE-3
- **Veo_3.1**: Google's video generation model

## Requirements

### Requirement 1: Creative Brief Input Processing

**User Story:** As a content creator, I want to provide a creative brief with specific parameters, so that the system can generate targeted advertisement videos.

#### Acceptance Criteria

1. WHEN a creative brief is provided, THE System SHALL accept the following required fields: theme, brand_name, target_duration_sec (30 or 60), aspect_ratio, and platform
2. WHEN target_duration_sec is 30, THE System SHALL generate 4-6 scenes
3. WHEN target_duration_sec is 60, THE System SHALL generate 6-10 scenes
4. WHEN optional fields are provided (tone, target_audience, key_message, call_to_action), THE System SHALL incorporate them into generation
5. THE System SHALL validate that target_duration_sec is either 30 or 60 seconds

### Requirement 2: Concept and Screenplay Generation

**User Story:** As a content creator, I want the system to generate creative concepts and screenplays, so that I have a narrative foundation for my video.

#### Acceptance Criteria

1. THE System SHALL preserve the existing ad_concept_creation_node functionality
2. THE System SHALL preserve the existing parallel screenplay generation nodes (Rajamouli and Shankar styles)
3. WHEN auto_select_screenplay mode is enabled, THE System SHALL automatically select the best screenplay based on evaluation criteria
4. WHEN auto_select_screenplay mode is disabled, THE System SHALL use the existing manual screenplay_evaluation_node for human selection
5. THE System SHALL maintain the existing State structure with theme, concept, screenplay_1, screenplay_2, and screenplay_winner fields

### Requirement 3: Scene Breakdown with Strict JSON Structure

**User Story:** As a system architect, I want scenes to follow a strict JSON structure, so that downstream nodes can reliably process scene data.

#### Acceptance Criteria

1. THE System SHALL add a scene_breakdown_node after screenplay selection
2. WHEN processing a 30-second video, THE Scene_Breakdown_Node SHALL generate 4-6 scenes
3. WHEN processing a 60-second video, THE Scene_Breakdown_Node SHALL generate 6-10 scenes
4. THE System SHALL enforce the following JSON schema for each scene: {scene_number: int, duration_sec: float, visual_description: str, audio_description: str, text_overlay: str}
5. THE System SHALL validate that the sum of all scene durations equals target_duration_sec (±2 seconds tolerance)
6. THE System SHALL add a scenes field to the State TypedDict

### Requirement 4: Storyboard Frame Generation with Gemini 2.5 Flash

**User Story:** As a content creator, I want storyboard frames generated using Gemini 2.5 Flash, so that I have high-quality visual representations of each scene.

#### Acceptance Criteria

1. THE System SHALL replace DALLE-3 with Gemini 2.5 Flash in the story_board_creation_node
2. WHEN generating storyboard frames, THE System SHALL create one frame per scene
3. WHEN calling Gemini 2.5 Flash, THE System SHALL use the scene's visual_description as the prompt
4. THE System SHALL store generated frames with metadata linking them to their corresponding scenes
5. THE System SHALL add a storyboard_frames field to the State TypedDict containing a list of {scene_number: int, image_url: str, prompt: str}

### Requirement 5: Video Clip Generation with Veo 3.1

**User Story:** As a content creator, I want video clips generated for each scene using Veo 3.1, so that I have animated content for my advertisement.

#### Acceptance Criteria

1. THE System SHALL add a video_generation_node after storyboard frame generation
2. WHEN generating video clips, THE System SHALL create one clip per scene using Veo 3.1
3. WHEN calling Veo 3.1, THE System SHALL provide the scene's visual_description, duration_sec, and corresponding storyboard_frame as inputs
4. THE System SHALL respect the aspect_ratio specified in the creative brief
5. THE System SHALL store generated clips with metadata linking them to their corresponding scenes
6. THE System SHALL add a video_clips field to the State TypedDict containing a list of {scene_number: int, video_url: str, duration_sec: float}

### Requirement 6: Video Assembly with Text Overlays and Captions

**User Story:** As a content creator, I want video clips assembled into a final MP4 with text overlays and captions, so that I have a complete advertisement ready for distribution.

#### Acceptance Criteria

1. THE System SHALL add a video_assembly_node after video clip generation
2. WHEN assembling the video, THE System SHALL concatenate video clips in scene_number order
3. WHEN a scene has a text_overlay field, THE System SHALL render the text on the video during that scene's duration
4. WHEN audio_description is provided, THE System SHALL generate captions for accessibility
5. THE System SHALL output a final MP4 file with the specified aspect_ratio
6. THE System SHALL add a final_video_url field to the State TypedDict

### Requirement 7: Quality Control Validation

**User Story:** As a system operator, I want automated quality control checks, so that generated videos meet minimum quality standards.

#### Acceptance Criteria

1. THE System SHALL add a qc_validation_node after video assembly
2. WHEN validating the video, THE System SHALL check that total duration matches target_duration_sec (±2 seconds tolerance)
3. WHEN validating the video, THE System SHALL verify that all scenes have corresponding video clips
4. WHEN validating the video, THE System SHALL check that the aspect_ratio matches the creative brief
5. IF validation fails, THEN THE System SHALL log errors and mark overall_status as "QC_FAILED"
6. IF validation passes, THEN THE System SHALL mark overall_status as "QC_PASSED"

### Requirement 8: Manifest Generation with Full Lineage

**User Story:** As a system operator, I want a manifest.json file with complete lineage, so that I can track all inputs, outputs, and processing steps.

#### Acceptance Criteria

1. THE System SHALL add a manifest_generation_node after QC validation
2. THE Manifest SHALL include the complete creative brief
3. THE Manifest SHALL include all generated artifacts (concept, screenplays, scenes, frames, clips, final_video)
4. THE Manifest SHALL include timestamps for each processing step
5. THE Manifest SHALL include model versions (Gemini 2.5 Flash, Veo 3.1)
6. THE System SHALL write the manifest to a manifest.json file
7. THE System SHALL add a manifest_url field to the State TypedDict

### Requirement 9: Human-in-the-Loop Checkpoints

**User Story:** As a content creator, I want configurable human review checkpoints, so that I can approve or modify content at key stages.

#### Acceptance Criteria

1. WHERE HITL checkpoints are enabled, THE System SHALL pause after screenplay selection for human approval
2. WHERE HITL checkpoints are enabled, THE System SHALL pause after storyboard frame generation for human approval
3. WHERE HITL checkpoints are enabled, THE System SHALL pause after video clip generation for human approval
4. WHEN a checkpoint is reached, THE System SHALL display current artifacts and prompt for approval
5. IF the user rejects at a checkpoint, THEN THE System SHALL allow regeneration of that stage

### Requirement 10: Safety Checks and Automated QC

**User Story:** As a system operator, I want safety checks throughout the pipeline, so that inappropriate or harmful content is detected and blocked.

#### Acceptance Criteria

1. THE System SHALL add safety validation after concept generation
2. THE System SHALL add safety validation after screenplay generation
3. THE System SHALL add safety validation after storyboard frame generation
4. THE System SHALL add safety validation after video clip generation
5. WHEN safety violations are detected, THE System SHALL halt processing and log the violation
6. THE System SHALL use content safety APIs to detect violence, hate speech, adult content, and brand safety violations

### Requirement 11: LangGraph State Management

**User Story:** As a system architect, I want the State TypedDict extended to support new pipeline stages, so that all data flows correctly through the graph.

#### Acceptance Criteria

1. THE System SHALL extend the State TypedDict to include: creative_brief, auto_select_screenplay, scenes, storyboard_frames, video_clips, final_video_url, manifest_url, qc_status, safety_status
2. THE System SHALL preserve existing State fields: theme, concept, screenplay_1, screenplay_2, screenplay_winner, story_board, overall_status
3. THE System SHALL use Annotated types with operator.add for fields that accumulate status messages
4. THE System SHALL maintain type safety throughout the pipeline
5. THE System SHALL validate State structure at each node transition

### Requirement 12: Error Handling and Retry Logic

**User Story:** As a system operator, I want robust error handling and retry logic, so that transient failures don't cause complete pipeline failures.

#### Acceptance Criteria

1. WHEN a node encounters a transient error (API timeout, rate limit), THE System SHALL retry up to 3 times with exponential backoff
2. WHEN a node encounters a permanent error (invalid input, safety violation), THE System SHALL halt processing and log the error
3. WHEN an error occurs, THE System SHALL update overall_status with error details
4. THE System SHALL preserve partial results in State even when errors occur
5. THE System SHALL provide clear error messages indicating which node failed and why
