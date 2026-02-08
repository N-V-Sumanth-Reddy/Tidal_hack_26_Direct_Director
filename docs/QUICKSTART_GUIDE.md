# Virtual Ad Agency - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.8+
- Node.js 18+
- TAMUS API key

---

## Step 1: Clone & Setup (1 min)

```bash
# Navigate to project directory
cd virtual-ad-agency

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd virtual-ad-agency-ui
npm install
cd ..
```

---

## Step 2: Configure Environment (1 min)

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API key
nano .env
```

Add this line:
```bash
TAMUS_API_KEY=your_actual_api_key_here
```

Save and exit (Ctrl+X, Y, Enter)

---

## Step 3: Start Backend (1 min)

```bash
cd backend
python main.py
```

✅ You should see:
```
✓ Loaded environment variables
✓ Successfully imported TAMUS wrapper
INFO:     Uvicorn running on http://0.0.0.0:2501
```

---

## Step 4: Start Frontend (1 min)

Open a **new terminal** window:

```bash
cd virtual-ad-agency-ui
npm run dev
```

✅ You should see:
```
▲ Next.js 16.1.6
- Local:        http://localhost:2500
✓ Ready in 2.3s
```

---

## Step 5: Use the Application (1 min)

1. Open browser: **http://localhost:2500**
2. Click **"New Project"**
3. Fill in project details
4. Click **"Create Project"**
5. Follow the workflow!

---

## 🎯 Complete Workflow Example

### 1. Create Project
```
Name: Summer Campaign
Client: TechCorp
Budget Band: Medium
Tags: tech, summer, lifestyle
```

### 2. Submit Brief
```
Platform: YouTube
Duration: 30 seconds
Budget: $50,000
Location: Urban cityscape
Creative Direction: Modern, energetic ad showcasing product features
Target Audience: Tech-savvy millennials aged 25-35
Brand Mandatories: Logo visible for 3 seconds, Use brand colors
Constraints: No animals, Daytime shooting only
```

### 3. Generate Concept
- Click **"Generate Concept"**
- Wait ~15 seconds
- Review AI-generated concept
- Click **"Generate Screenplays"**

### 4. Compare Screenplays
- Wait ~25 seconds
- Review both variants:
  - **Variant A:** Rajamouli Style (Epic, Grand Scale)
  - **Variant B:** Shankar Style (High-Tech, Futuristic)
- Select your preferred variant
- Click **"Select"**

### 5. Generate Storyboard
- Click **"Generate Storyboard"**
- Wait ~20 seconds
- Review storyboard scenes
- Click **"Generate Production Pack"**

### 6. Review Production Pack
- Wait ~25 seconds
- Review:
  - Budget estimate (min/max)
  - Production schedule
  - Crew requirements
  - Locations
  - Equipment list

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt

# Check if port 2501 is available
lsof -i :2501
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check if port 2500 is available
lsof -i :2500
```

### API Key Issues
```bash
# Verify .env file exists
ls -la .env

# Check if API key is set
cat .env | grep TAMUS_API_KEY

# Make sure no spaces around the = sign
# CORRECT: TAMUS_API_KEY=abc123
# WRONG:   TAMUS_API_KEY = abc123
```

### Generation Fails
1. Check backend terminal for errors
2. Check browser console (F12) for errors
3. Verify TAMUS API key is valid
4. Check internet connection

---

## 📚 Next Steps

### Learn More
- Read `SYSTEM_STATUS.md` for complete system overview
- Read `LANGGRAPH_FLOW_EXPLAINED.md` to understand the pipeline
- Read `BACKEND_FRONTEND_TYPE_MAPPING.md` for API reference

### Customize
- Modify screenplay styles in `backend/main.py`
- Customize UI components in `virtual-ad-agency-ui/components/`
- Add new generation steps in the pipeline

### Deploy
- Add database for persistence
- Add authentication for security
- Deploy backend to cloud (AWS, GCP, Azure)
- Deploy frontend to Vercel or Netlify

---

## 🎓 Key Concepts

### Workflow Steps
1. **Brief** - Define project requirements
2. **Concept** - AI generates creative concept
3. **Screenplays** - AI generates 2 style variants
4. **Select** - Choose winning screenplay
5. **Storyboard** - AI generates scene-by-scene breakdown
6. **Production** - AI generates production documents
7. **Export** - Download deliverables

### AI Models Used
- **TAMUS GPT-5.2** - Text generation (concepts, screenplays, production)
- **Gemini 2.5 Flash** - Image generation (storyboards - when pipeline integrated)

### Screenplay Styles
- **Rajamouli Style** - Epic, grand scale, dramatic, mythological undertones
- **Shankar Style** - High-tech, futuristic, innovative, social message

---

## 💡 Tips & Tricks

### Better Results
1. **Be specific in briefs** - More detail = better AI output
2. **Use clear creative direction** - Describe the mood and style
3. **Set realistic budgets** - Helps AI generate feasible plans
4. **Review each step** - AI works best with human guidance

### Faster Workflow
1. **Use templates** - Save common brief configurations
2. **Batch projects** - Create multiple projects at once
3. **Keyboard shortcuts** - Navigate faster through UI
4. **Save favorites** - Bookmark frequently used settings

### Common Patterns
```
Low Budget ($10k-30k)
- Simple locations
- Small crew
- Minimal equipment
- 1-2 shoot days

Medium Budget ($30k-100k)
- Multiple locations
- Professional crew
- Standard equipment
- 2-5 shoot days

High Budget ($100k-500k)
- Premium locations
- Large crew
- Advanced equipment
- 5-10 shoot days
```

---

## 🆘 Getting Help

### Documentation
1. `SYSTEM_STATUS.md` - System overview
2. `FINAL_STATUS_REPORT.md` - Complete status
3. `LANGGRAPH_FLOW_EXPLAINED.md` - Pipeline details
4. `BACKEND_FRONTEND_TYPE_MAPPING.md` - API reference

### Common Issues
- **"Connection refused"** - Backend not running
- **"404 Not Found"** - Wrong URL or port
- **"Generation failed"** - Check API key
- **"TypeScript errors"** - Run `npm run build` to check

### Debug Mode
```bash
# Backend verbose logging
export QUIET_MODE=false
cd backend
python main.py

# Frontend debug mode
cd virtual-ad-agency-ui
npm run dev -- --debug
```

---

## ✅ Verification Checklist

Before starting, verify:
- [ ] Python 3.8+ installed
- [ ] Node.js 18+ installed
- [ ] Dependencies installed (pip & npm)
- [ ] .env file created with TAMUS_API_KEY
- [ ] Backend starts on port 2501
- [ ] Frontend starts on port 2500
- [ ] Browser can access http://localhost:2500

---

## 🎉 You're Ready!

The system is now running. Create your first project and explore the AI-powered ad production workflow!

**Happy Creating! 🚀**

---

*For detailed information, see SYSTEM_STATUS.md*
*For troubleshooting, see FINAL_STATUS_REPORT.md*
