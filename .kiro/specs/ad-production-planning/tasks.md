# Implementation Plan: Ad Production Multi-Agent System

## Overview

This implementation plan converts the ad production planning design into discrete coding tasks. The system extends the existing ad_video_pipeline.py by removing video generation and adding production planning nodes. Tasks are organized to build incrementally, with testing integrated throughout.

## Tasks

- [x] 1. Set up project structure and extend State TypedDict
  - Create new file `ad_production_pipeline.py` that imports from `ad_video_pipeline.py`
  - Extend State TypedDict with new fields: scene_plan, locations_plan, budget_estimate, schedule_plan, casting_suggestions, props_wardrobe_list, legal_clearance_report, risk_register, production_pack
  - Create data model files in `models/` directory: scene_plan.py, locations_plan.py, budget_estimate.py, schedule_plan.py, crew_gear.py, legal_clearance.py, risk_register.py
  - Define TypedDict classes for: Shot, SceneDetail, ScenePlan, LocationRequirement, LocationsPlan, BudgetLineItem, BudgetEstimate, ScheduleDay, SchedulePlan, CrewMember, EquipmentItem, CrewGearPackage, LegalItem, LegalClearanceReport, Risk, RiskRegister
  - _Requirements: 14.1, 14.2, 14.3_

- [x] 2. Implement scene breakdown node with JSON schema validation
  - [x] 2.1 Create scene_breakdown_node function
    - Write node function that takes State and returns Dict with scene_plan
    - Use LLM to generate scene plan from storyboard_frames
    - Implement prompt template for scene breakdown (see design document)
    - Parse LLM JSON response and validate against ScenePlan schema
    - Validate scene count (4-6 for 30s, 6-10 for 60s)
    - Validate shot durations sum to scene duration (±1 second tolerance)
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ]* 2.2 Write property test for scene plan schema compliance
    - **Property 2: Scene Plan Schema Compliance**
    - **Validates: Requirements 3.2, 3.3**
  
  - [ ]* 2.3 Write property test for shot duration invariant
    - **Property 3: Shot Duration Invariant**
    - **Validates: Requirements 3.4**
  
  - [ ]* 2.4 Write property test for scene plan JSON schema validation
    - **Property 30: Scene Plan JSON Schema Validation**
    - **Validates: Requirements 16.2**

- [x] 3. Implement scene plan approval gate (HITL)
  - Create scene_plan_approval_gate function
  - Display scene_plan.json in readable format with summary statistics
  - Prompt user for approval/rejection
  - Handle rejection with modification support
  - Return approval status and optional modifications
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 4. Checkpoint - Ensure scene breakdown and approval gate work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement location planning node
  - [x] 5.1 Create location_planning_node function
    - Write node function that takes State with scene_plan and returns Dict with locations_plan
    - Extract unique locations from scene_plan
    - Use LLM to generate location requirements, alternates, and permit checklist
    - Implement prompt template for location planning (see design document)
    - Parse LLM response and validate against LocationsPlan schema
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [ ] 5.2 Create markdown and JSON exporters for locations plan
    - Write markdown_exporter.py with function to export locations plan as markdown
    - Write json_exporter.py with function to export locations plan as JSON
    - _Requirements: 6.5_
  
  - [ ]* 5.3 Write property test for location count correspondence
    - **Property 5: Location Count Correspondence**
    - **Validates: Requirements 6.1**
  
  - [ ]* 5.4 Write property test for locations plan schema compliance
    - **Property 6: Locations Plan Schema Compliance**
    - **Validates: Requirements 6.2, 6.4**
  
  - [ ]* 5.5 Write property test for location alternates presence
    - **Property 7: Location Alternates Presence**
    - **Validates: Requirements 6.3**

- [ ] 6. Implement budget estimation node
  - [x] 6.1 Create budgeting_node function
    - Write node function that takes State with scene_plan and returns Dict with budget_estimate
    - Implement budget calculation logic (see design document)
    - Calculate line items for: crew, equipment, location fees, talent, props/wardrobe, post-production, insurance, contingency
    - Generate min/max ranges for each line item
    - Include explicit assumptions and cost drivers
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [ ] 6.2 Create markdown and CSV exporters for budget estimate
    - Write csv_exporter.py with function to export budget estimate as CSV
    - Update markdown_exporter.py with function to export budget estimate as markdown
    - _Requirements: 7.5_
  
  - [ ]* 6.3 Write property test for budget range validity
    - **Property 8: Budget Range Validity**
    - **Validates: Requirements 7.1**
  
  - [ ]* 6.4 Write property test for budget category completeness
    - **Property 9: Budget Category Completeness**
    - **Validates: Requirements 7.2**
  
  - [ ]* 6.5 Write property test for budget assumptions presence
    - **Property 10: Budget Assumptions Presence**
    - **Validates: Requirements 7.3, 7.4, 16.3**

- [ ] 7. Implement schedule planning node
  - [x] 7.1 Create schedule_ad_node function
    - Write node function that takes State with scene_plan and returns Dict with schedule_plan
    - Implement scheduling algorithm (see design document)
    - Group scenes by location to minimize company moves
    - Estimate setup time, shoot time, and company move time
    - Split scenes across multiple days if total time > 10 hours
    - Include explicit assumptions
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [ ] 7.2 Create markdown and CSV exporters for schedule plan
    - Update csv_exporter.py with function to export schedule plan as CSV
    - Update markdown_exporter.py with function to export schedule plan as markdown
    - _Requirements: 8.5_
  
  - [ ]* 7.3 Write property test for schedule days estimation
    - **Property 11: Schedule Days Estimation**
    - **Validates: Requirements 8.1**
  
  - [ ]* 7.4 Write property test for scene location grouping
    - **Property 12: Scene Location Grouping**
    - **Validates: Requirements 8.2**
  
  - [ ]* 7.5 Write property test for setup time presence
    - **Property 13: Setup Time Presence**
    - **Validates: Requirements 8.3**
  
  - [ ]* 7.6 Write property test for company move time between locations
    - **Property 14: Company Move Time Between Locations**
    - **Validates: Requirements 8.4**
  
  - [ ]* 7.7 Write property test for schedule assumptions presence
    - **Property 15: Schedule Assumptions Presence**
    - **Validates: Requirements 16.4**

- [x] 8. Checkpoint - Ensure location, budget, and schedule nodes work
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement casting suggestions node
  - Create casting_node function
  - Extract cast requirements from scene_plan (cast_count, character descriptions)
  - Use LLM to generate casting breakdown with character descriptions, age ranges, and attributes
  - Suggest casting approach (professional actors, non-actors, brand ambassadors)
  - Include notes on special requirements (stunts, special skills)
  - _Requirements: 9.1, 9.5_

- [x] 10. Implement props and wardrobe node
  - Create props_wardrobe_node function
  - Extract all props and wardrobe items from scene_plan
  - Organize by scene and category
  - Include quantity, source (purchase, rental, on-hand), and estimated cost
  - Flag items requiring special handling or advance procurement
  - _Requirements: 9.1, 9.5_

- [x] 11. Implement crew and gear suggestions node
  - [x] 11.1 Create crew_gear_node function
    - Write node function that takes State with scene_plan and returns Dict with crew_gear_package
    - Generate minimum viable crew list with roles and responsibilities
    - Generate minimum viable equipment list
    - Include optional upgrades for crew and equipment (marked with required=False)
    - Base recommendations on scene complexity, location types, and technical requirements
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ]* 11.2 Write property test for crew gear schema compliance
    - **Property 16: Crew Gear Schema Compliance**
    - **Validates: Requirements 9.2, 9.3**
  
  - [ ]* 11.3 Write property test for crew gear upgrades presence
    - **Property 17: Crew Gear Upgrades Presence**
    - **Validates: Requirements 9.4**

- [ ] 12. Implement legal clearances node
  - [x] 12.1 Create legal_clearance_node function
    - Write node function that takes State with scene_plan and returns Dict with legal_clearance_report
    - Implement legal risk assessment logic (see design document)
    - Identify talent releases required (based on cast_count)
    - Identify location releases required (based on location types)
    - Scan scene descriptions for trademarks, logos, branded products
    - Identify music rights requirements
    - Check for claims/substantiation requirements
    - Flag if minors involved or drone permits required
    - Mark high-risk items requiring legal review
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [ ] 12.2 Create markdown exporter for legal clearance report
    - Update markdown_exporter.py with function to export legal clearance report as markdown
    - _Requirements: 10.5_
  
  - [ ]* 12.3 Write property test for legal clearance schema compliance
    - **Property 18: Legal Clearance Schema Compliance**
    - **Validates: Requirements 10.2**
  
  - [ ]* 12.4 Write property test for talent releases for cast
    - **Property 19: Talent Releases for Cast**
    - **Validates: Requirements 10.3**
  
  - [ ]* 12.5 Write property test for high-risk legal items flagged
    - **Property 20: High-Risk Legal Items Flagged**
    - **Validates: Requirements 10.4**

- [ ] 13. Implement risk and safety node
  - [x] 13.1 Create risk_safety_node function
    - Write node function that takes State with scene_plan and returns Dict with risk_register
    - Implement risk assessment logic (see design document)
    - Identify safety hazards based on scene content
    - Assess weather risks for exterior scenes
    - Assess night shoot risks
    - Assess stunt risks
    - Assess crowd management risks
    - Assess equipment risks
    - For each risk, provide likelihood, impact, and mitigation strategy
    - _Requirements: 11.1, 11.2, 11.3, 11.4_
  
  - [ ] 13.2 Create markdown exporter for risk register
    - Update markdown_exporter.py with function to export risk register as markdown
    - _Requirements: 11.5_
  
  - [ ]* 13.3 Write property test for risk register schema compliance
    - **Property 21: Risk Register Schema Compliance**
    - **Validates: Requirements 11.3**
  
  - [ ]* 13.4 Write property test for weather risks for exterior scenes
    - **Property 22: Weather Risks for Exterior Scenes**
    - **Validates: Requirements 11.4**

- [x] 14. Checkpoint - Ensure all parallel planning nodes work
  - Ensure all tests pass, ask the user if questions arise.

- [x] 15. Implement budget and schedule approval gate (HITL)
  - Create budget_schedule_approval_gate function
  - Display budget estimate with total range and key line items
  - Display schedule plan with total shoot days and key milestones
  - Prompt user for approval/rejection
  - Handle rejection with constraint modification support
  - Return approval status and optional constraint changes
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 16. Implement client review pack generation node
  - [x] 16.1 Create client_review_pack_node function
    - Write node function that takes complete State and returns Dict with production_pack path
    - Generate single markdown document with table of contents
    - Include executive summary with key metrics
    - Embed storyboard frames with links
    - Include scene plan summary table
    - Include shotlist table
    - Include locations plan with requirements and alternates
    - Include budget estimate table
    - Include schedule plan table
    - Include crew and gear recommendations
    - Include legal clearances checklist
    - Include risk register
    - Note any missing artifacts
    - _Requirements: 13.1, 13.2, 13.3, 13.4_
  
  - [ ] 16.2 Create PDF exporter for production pack
    - Write pdf_exporter.py with function to export production pack as PDF using pandoc
    - _Requirements: 13.5_
  
  - [ ]* 16.3 Write property test for production pack structure completeness
    - **Property 23: Production Pack Structure Completeness**
    - **Validates: Requirements 13.2, 13.3, 13.4**
  
  - [ ]* 16.4 Write property test for production pack missing artifacts notation
    - **Property 32: Production Pack Missing Artifacts Notation**
    - **Validates: Requirements 17.3**

- [ ] 17. Implement LangGraph pipeline with parallel execution
  - [ ] 17.1 Create StateGraph with all nodes
    - Import preserved creative chain nodes from ad_video_pipeline.py
    - Add scene_breakdown_node
    - Add scene_plan_approval_gate
    - Add parallel planning nodes: location_planning_node, budgeting_node, schedule_ad_node, casting_node, props_wardrobe_node, crew_gear_node, legal_clearance_node, risk_safety_node
    - Add budget_schedule_approval_gate
    - Add client_review_pack_node
    - _Requirements: 5.1, 5.2_
  
  - [ ] 17.2 Configure graph edges for parallel execution
    - Connect creative chain nodes (concept → screenplays → evaluation → storyboard)
    - Connect storyboard → scene_breakdown → scene_plan_approval_gate
    - Connect scene_plan_approval_gate → parallel planning nodes (fan-out)
    - Connect all parallel planning nodes → budget_schedule_approval_gate (fan-in)
    - Connect budget_schedule_approval_gate → client_review_pack_node
    - _Requirements: 5.1, 5.2, 5.4_
  
  - [ ] 17.3 Implement error handling for parallel nodes
    - Wrap each parallel node in try-except block
    - Log errors to overall_status
    - Mark failed artifacts as unavailable
    - Continue execution of other parallel nodes on failure
    - _Requirements: 5.3, 17.1, 17.2, 17.4_
  
  - [ ]* 17.4 Write property test for parallel node error isolation
    - **Property 4: Parallel Node Error Isolation**
    - **Validates: Requirements 5.3, 17.1**
  
  - [ ]* 17.5 Write property test for error logging on node failure
    - **Property 31: Error Logging on Node Failure**
    - **Validates: Requirements 17.2, 17.4**

- [ ] 18. Implement regeneration support with constraint modification
  - [ ] 18.1 Add regeneration logic to approval gates
    - Modify scene_plan_approval_gate to support regeneration with modifications
    - Modify budget_schedule_approval_gate to support constraint changes
    - Preserve storyboard_frames when regenerating
    - Preserve scene_plan when regenerating budget/schedule (unless explicitly modified)
    - _Requirements: 15.1, 15.2, 15.5_
  
  - [ ] 18.2 Implement constraint modification handlers
    - Handle budget constraint changes (reduce budget by X%, change crew rates, etc.)
    - Handle schedule constraint changes (compress to X days, change shoot hours, etc.)
    - Regenerate affected artifacts (budget_estimate, schedule_plan)
    - _Requirements: 15.3, 15.4_
  
  - [ ]* 18.3 Write property test for storyboard preservation on regeneration
    - **Property 25: Storyboard Preservation on Regeneration**
    - **Validates: Requirements 15.1**
  
  - [ ]* 18.4 Write property test for scene plan preservation on regeneration
    - **Property 26: Scene Plan Preservation on Regeneration**
    - **Validates: Requirements 15.2**
  
  - [ ]* 18.5 Write property test for budget regeneration on constraint change
    - **Property 27: Budget Regeneration on Constraint Change**
    - **Validates: Requirements 15.3**
  
  - [ ]* 18.6 Write property test for schedule regeneration on constraint change
    - **Property 28: Schedule Regeneration on Constraint Change**
    - **Validates: Requirements 15.4**

- [ ] 19. Checkpoint - Ensure full pipeline works end-to-end
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 20. Implement validators for State transitions
  - [ ] 20.1 Create state validators
    - Write scene_plan_validator.py to validate scene plan structure
    - Write budget_validator.py to validate budget estimate structure
    - Write schedule_validator.py to validate schedule plan structure
    - _Requirements: 14.4, 14.5_
  
  - [ ] 20.2 Add validation at node transitions
    - Validate State structure before each node execution
    - Check that all required fields for that stage are present
    - Raise clear error messages if validation fails
    - _Requirements: 14.5_
  
  - [ ]* 20.3 Write property test for state validation at transitions
    - **Property 24: State Validation at Transitions**
    - **Validates: Requirements 14.5**

- [ ] 21. Implement dual-format export for all artifacts
  - [ ] 21.1 Complete all exporters
    - Ensure markdown_exporter.py handles all artifact types
    - Ensure csv_exporter.py handles shotlist, budget, and schedule
    - Ensure json_exporter.py handles locations plan and scene plan
    - Ensure pdf_exporter.py handles production pack
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5_
  
  - [ ]* 21.2 Write property test for dual-format export compliance
    - **Property 33: Dual-Format Export Compliance**
    - **Validates: Requirements 6.5, 7.5, 8.5, 10.5, 11.5, 13.5, 18.1, 18.2, 18.3, 18.4, 18.5**

- [ ] 22. Implement end-to-end integration tests
  - [ ]* 22.1 Write property test for end-to-end artifact generation
    - **Property 29: End-to-End Artifact Generation**
    - **Validates: Requirements 16.1, 16.5**
  
  - [ ]* 22.2 Write integration test for approval flow
    - Test complete pipeline with scene plan approval
    - Test complete pipeline with budget/schedule approval
    - _Requirements: 4.3, 12.3_
  
  - [ ]* 22.3 Write integration test for rejection flow
    - Test scene plan rejection and regeneration
    - Test budget/schedule rejection and regeneration
    - _Requirements: 4.4, 12.4_
  
  - [ ]* 22.4 Write integration test for constraint modification
    - Test budget constraint change and regeneration
    - Test schedule constraint change and regeneration
    - _Requirements: 15.3, 15.4_

- [ ] 23. Implement Gemini 2.5 Flash verification
  - [ ]* 23.1 Write property test for Gemini 2.5 Flash API usage
    - **Property 1: Gemini 2.5 Flash API Usage**
    - **Validates: Requirements 1.5**

- [ ] 24. Create test data generators for property tests
  - Create generate_random_scene_plan function (see design document)
  - Create generate_random_locations_plan function
  - Create generate_random_budget_estimate function
  - Create generate_random_schedule_plan function
  - Create generate_random_legal_clearance_report function
  - Create generate_random_risk_register function

- [ ] 25. Final checkpoint - Ensure all tests pass
  - Run full test suite with property tests (100 iterations each)
  - Verify all 33 correctness properties pass
  - Verify all integration tests pass
  - Verify end-to-end pipeline completes successfully
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 26. Create example notebook demonstrating the pipeline
  - Create Jupyter notebook showing complete pipeline execution
  - Include example with 30-second ad
  - Include example with 60-second ad
  - Show HITL gate interactions
  - Show regeneration with constraint changes
  - Display all generated artifacts

## Notes

- Tasks marked with `*` are optional test tasks and can be skipped for faster MVP
- Each property test references a specific property from the design document
- Property tests should run minimum 100 iterations to ensure comprehensive coverage
- Checkpoints ensure incremental validation throughout implementation
- The pipeline preserves the existing creative chain (concept → screenplays → storyboard) without modification
- Video generation functionality (Veo 3.1, FFmpeg) is explicitly removed
- Parallel planning nodes execute concurrently for efficiency
- HITL gates allow human review and approval at critical decision points
- Regeneration support allows constraint modification without redoing the entire pipeline
