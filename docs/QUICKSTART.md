# Quick Start Guide

## 1. Setup Environment

Create `.env` file in project root:

```bash
# Required
TAMUS_API_KEY=your_key_here
TAMUS_API_URL=https://chat-api.tamu.ai
TAMUS_MODEL=protected.gpt-5.2
USE_TAMUS_API=true

# Optional
GEMINI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

## 2. Start Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

✅ Backend running on: **http://localhost:2501**

## 3. Start Frontend

```bash
cd virtual-ad-agency-ui
npm install
npm run dev
```

✅ Frontend running on: **http://localhost:2500**

## 4. Use Application

Open: **http://localhost:2500**

### Workflow

1. **Create Project** → Name: "EcoPhone Campaign"
2. **Submit Brief** → (default values pre-filled)
3. **Generate Concept** → Wait 10-30s
4. **Generate Screenplays** → Wait 15-40s
5. **Select Screenplay** → Click "Select" on one variant
6. **Generate Storyboard** → Wait 10-20s
7. **Generate Production Pack** → Wait 10-20s

## Expected Times

| Step | Time |
|------|------|
| Concept | 10-30s |
| Screenplays | 15-40s |
| Storyboard | 10-20s |
| Production | 10-20s |

## Troubleshooting

### Backend Error

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Error

```bash
cd virtual-ad-agency-ui
npm install
npm run dev
```

### Concept Not Showing

- Check backend logs for errors
- Check browser console (F12)
- Wait 60 seconds (polling timeout)
- Verify TAMUS_API_KEY is set

## API Documentation

Backend API docs: **http://localhost:2501/docs**

## Support

See README.md for detailed documentation.
