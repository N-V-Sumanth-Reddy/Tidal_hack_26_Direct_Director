# Changelog

## [2.0.0] - 2025-02-07

### Refactored - Code Cleanup

**Removed unnecessary files to simplify codebase:**

#### Pipeline Files (Not Used)
- `ad_video_pipeline.py` - Full video generation pipeline (not needed)
- `ad_production_pipeline.py` - Production pipeline with manual gates (not needed)
- Backend now generates all content directly with TAMUS API

#### Test Files
- `test_*.py` - All test scripts (20+ files)
- `test_*.sh` - Test shell scripts
- `check_*.py` - API check scripts
- `visualize_*.py` - Pipeline visualization scripts
- `generate_storyboard.py` - Standalone storyboard generator
- `inspect_veo_operation.py` - VEO API inspector
- `cost_tracker.py` - Cost tracking utility

#### Documentation Files
- `*.md` - 30+ old documentation files
- Replaced with clean README.md and QUICKSTART.md

#### Other Files
- `05_movie_storyboarding.ipynb` - Jupyter notebook
- `test_image.png` - Test image

### Current Structure

```
.
├── backend/                 # FastAPI backend
├── virtual-ad-agency-ui/   # Next.js frontend
├── models/                 # Data models
├── tamus_wrapper.py       # TAMUS API client
├── .env                   # Environment config
├── README.md              # Main documentation
├── QUICKSTART.md          # Quick start guide
└── CHANGELOG.md           # This file
```

### What's Working

✅ Full workflow: Brief → Concept → Screenplays → Storyboard → Production Pack
✅ All generation uses TAMUS API directly (no complex pipelines)
✅ Job status polling (automatic retry)
✅ Error handling and fallbacks
✅ Clean, maintainable codebase

### Breaking Changes

- Removed `ad_video_pipeline.py` and `ad_production_pipeline.py`
- Backend no longer imports or uses these pipelines
- All generation is now direct TAMUS API calls

### Migration Guide

No migration needed - the backend was already updated to not use the removed files.

## [1.0.0] - 2025-02-06

### Added

- Initial release
- Full-stack application (FastAPI + Next.js)
- TAMUS integration for text generation
- Job status polling
- Production pack generation

### Fixed

- Concept not showing in UI (polling fix)
- Production pack blocking (removed pipeline)
- Screenplays showing 0 scenes (polling fix)
- Storyboard not updating (polling fix)
