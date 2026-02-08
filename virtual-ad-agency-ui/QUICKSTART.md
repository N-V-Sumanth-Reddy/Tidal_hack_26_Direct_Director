# Virtual Ad Agency UI - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ installed
- Backend server running on `http://localhost:8000`

### Installation

```bash
cd virtual-ad-agency-ui
npm install
```

### Running the Application

```bash
# Development mode (runs on port 2500)
npm run dev

# Production build
npm run build
npm start
```

### Running Tests

```bash
# Run tests
npm test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

## 📱 Application Structure

### Pages

1. **Home** (`/`) - Redirects to projects
2. **Projects** (`/projects`) - List all projects with filters
3. **Workspace** (`/workspace/[projectId]`) - Project workspace with workflow steps

### Workflow Steps

1. **Brief** - Submit project brief with requirements
2. **Concept** - View AI-generated creative concept
3. **Screenplays** - Compare two screenplay variants
4. **Select** - Choose winning screenplay (HITL gate)
5. **Storyboard** - View storyboard scenes (coming soon)
6. **Production** - Production pack dashboard (coming soon)
7. **Export** - Export deliverables (coming soon)

## 🎯 Testing the Application

### 1. Start the Backend

```bash
cd backend
python main.py
```

Backend will run on `http://localhost:8000`

### 2. Start the Frontend

```bash
cd virtual-ad-agency-ui
npm run dev
```

Frontend will run on `http://localhost:2500`

### 3. Test the Workflow

1. Open `http://localhost:2500`
2. You'll be redirected to `/projects`
3. Click "New Project" to create a project
4. Fill in the brief form:
   - Platform: YouTube
   - Duration: 30 seconds
   - Budget: $50,000
   - Location: Urban
   - Creative Direction: Modern tech product showcase
   - Target Audience: Millennials
5. Click "Submit Brief & Generate Concept"
6. Wait for concept generation (mock mode: 2 seconds)
7. Click "Generate Screenplays"
8. Compare the two screenplay variants
9. Click "Choose This Screenplay" on your preferred variant
10. Continue through remaining steps

## 🔧 Configuration

### API Endpoint

The frontend connects to the backend at `http://localhost:8000` by default.

To change this, update `virtual-ad-agency-ui/lib/api.ts`:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### Port Configuration

The frontend runs on port 2500 by default (configured in `package.json`).

To change the port:

```json
{
  "scripts": {
    "dev": "next dev -p YOUR_PORT",
    "start": "next start -p YOUR_PORT"
  }
}
```

## 🎨 Features Implemented

### ✅ Complete
- Project list with filters (status, budget, search)
- Project creation
- Brief submission form
- Concept display
- Screenplay comparison
- Screenplay selection (HITL gate)
- Workflow stepper navigation
- Dock navigation (macOS-style)
- Loading states and skeletons
- Progress indicators
- Streaming text display
- Warning banners
- Empty states
- Responsive design
- Type-safe API client
- React Query integration
- SSE streaming support

### 🚧 Coming Soon
- Storyboard viewer
- Production pack dashboard
- Budget/schedule editors
- Export functionality
- Real-time collaboration
- Version history

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 2500
lsof -ti:2500 | xargs kill -9

# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Backend Connection Issues

1. Verify backend is running: `curl http://localhost:8000`
2. Check CORS configuration in `backend/main.py`
3. Check browser console for errors

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## 📚 Tech Stack

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui
- **Animations**: Framer Motion, React Bits
- **State Management**: React Context + React Query
- **Testing**: Vitest + React Testing Library + fast-check
- **Icons**: Lucide React

## 🎓 Next Steps

1. **Test the full workflow** - Create a project and go through all steps
2. **Explore the API** - Open `http://localhost:8000/docs` for Swagger UI
3. **Run tests** - Execute `npm test` to see the test suite
4. **Customize** - Modify components to match your brand
5. **Deploy** - Build and deploy to your hosting platform

## 📖 Documentation

- [Implementation Status](./IMPLEMENTATION_STATUS.md) - What's built and what's next
- [Testing Guide](../TESTING_GUIDE.md) - How to test the backend
- [Backend README](../backend/README.md) - Backend API documentation

## 🤝 Contributing

This is a demo application. Feel free to:
- Add new features
- Improve existing components
- Write more tests
- Enhance the UI/UX

## 📝 License

MIT License - feel free to use this code in your projects!
