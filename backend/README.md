# FastAPI Backend for Virtual Ad Agency

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python main.py
```

The API will start at `http://localhost:8000`

### 3. Test the API

Open `http://localhost:8000/docs` to see the interactive API documentation (Swagger UI).

## API Endpoints

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/{id}` - Get project details
- `PATCH /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Brief
- `POST /api/projects/{id}/brief` - Submit brief

### Generation
- `POST /api/projects/{id}/generate/concept` - Generate concept
- `POST /api/projects/{id}/generate/screenplays` - Generate screenplays
- `POST /api/projects/{id}/generate/storyboard` - Generate storyboard
- `POST /api/projects/{id}/generate/production` - Generate production pack

### Selection
- `POST /api/projects/{id}/select/screenplay` - Select screenplay winner

### Jobs
- `GET /api/jobs/{id}` - Get job status
- `POST /api/jobs/{id}/cancel` - Cancel job
- `GET /api/stream/generation/{id}` - SSE stream for progress

## Testing with curl

### Create a Project
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign",
    "client": "Test Client",
    "tags": ["test"],
    "budgetBand": "medium"
  }'
```

### Submit a Brief
```bash
curl -X POST http://localhost:8000/api/projects/{PROJECT_ID}/brief \
  -H "Content-Type: application/json" \
  -d '{
    "brief": {
      "platform": "YouTube",
      "duration": 30,
      "budget": 50000,
      "location": "Urban",
      "constraints": [],
      "creativeDirection": "Modern and energetic",
      "brandMandatories": ["Logo visible"],
      "targetAudience": "Millennials"
    }
  }'
```

### Generate Concept
```bash
curl -X POST http://localhost:8000/api/projects/{PROJECT_ID}/generate/concept
```

## Pipeline Integration

The backend automatically imports your existing pipelines:
- `ad_video_pipeline.py` - For concept, screenplay, and storyboard generation
- `ad_production_pipeline.py` - For production pack generation

If the pipelines are not available, the backend runs in **mock mode** for testing.

## Mock Mode

When pipelines are not available, the backend generates mock data:
- Concepts with placeholder text
- Two screenplay variants with mock scores
- Mock storyboards and production packs

This allows you to test the full workflow without the actual pipelines.

## CORS Configuration

The backend allows requests from:
- `http://localhost:2500` (your frontend)
- `http://localhost:3000` (alternative port)

## Next Steps

1. **Test the API** - Use Swagger UI at `/docs`
2. **Connect Frontend** - The frontend is already configured to use this backend
3. **Add Real Pipelines** - Replace mock mode with your actual pipeline integration
4. **Add Database** - Replace in-memory storage with PostgreSQL/SQLite
5. **Add Authentication** - Implement JWT tokens for security

## Development

### Run with Auto-Reload
```bash
uvicorn main:app --reload --port 8000
```

### View Logs
The server logs all requests and errors to the console.

### Debug Mode
Set `debug=True` in `uvicorn.run()` for detailed error messages.
