# Idea Shaper

Transform rough ideas into structured project## Getting Started Guide

New users get an interactive onboarding experience:

- Automatically appears on first visit (dismissible)
- Access anytime from the header or main menu
- Covers core features, templates, search, insights, and shortcutswith AI-powered mentorship. Get thoughtful guidance through Socratic questioning and interactive refinement.

## Features

- **🧠 AI Mentorship** - Socratic questioning to refine your ideas naturally
- **📈 Structured Development** - Guided flow from concept to actionable proposal
- **💬 Modern Interface** - Clean, intuitive chat with rich formatting and animations
- **⚡ Multi-AI Support** - Powered by Gemini, GPT-4, and Claude for diverse perspectives
- **🔍 Market Research** - Automatic competitor analysis and industry insights
- **🗺️ Visual Mapping** - See concept relationships through interactive graphs
- **📊 Analytics Dashboard** - Track progress and conversation insights
- **⌨️ Keyboard Shortcuts** - Quick actions for power users (Alt+N, Alt+T, Alt+F, etc.)
- **💾 Export & Share** - Save conversations as JSON or Markdown

## Tech Stack

**Backend**

- FastAPI for high-performance async APIs
- Multi-AI support (Gemini, OpenAI, Anthropic)
- SQLAlchemy + SQLite for data persistence
- Market research APIs (News API, SERP, Crunchbase)
- NetworkX for visual concept mapping

**Frontend**

- Next.js 14 with TypeScript and App Router
- Tailwind CSS for responsive, modern styling
- Lucide React icons and date-fns utilities
- Markdown rendering with syntax highlighting

## Quick Start

**Prerequisites:** Python 3.8+, Node.js 18+

**Backend**

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Server runs at `http://localhost:8000`

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

App available at `http://localhost:3000`

## Keyboard Shortcuts

- **Enter** - Send message
- **Alt + N** - New conversation
- **Alt + K** - Focus input field
- **Alt + T** - Open templates
- **Alt + F** - Search conversations
- **Alt + I** - View insights
- **Alt + /** - Show all shortcuts
- **Esc** - Close modals

## In‑App Getting Started Guide

A guided onboarding is available inside the app to help new users:

- Open it from the header button near the Menu, or via Menu → Getting Started
- It appears automatically on your first visit (you can dismiss or choose "Don’t show again")
- Covers quick steps, core tools (Templates, Search, Insights, Export), and keyboard shortcuts

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── ai_service.py        # AI model integration
│   ├── models.py            # Data models
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── app/                 # Next.js App Router
│   ├── components/          # React components
│   ├── lib/                 # Utility functions
│   └── package.json         # Node.js dependencies
└── README.md
```

## Usage

1. Launch both backend and frontend servers
2. Navigate to `http://localhost:3000`
3. Share your idea - no matter how rough
4. Follow AI guidance through refinement stages
5. Export your structured proposal

## Key API Endpoints

- `POST /api/chat` - Send messages and get AI responses
- `GET /api/conversation/{id}` - Retrieve conversation history
- `POST /api/proposal/{id}` - Generate structured proposal
- `GET /health` - Service health check

## Development

Clean architecture with separation of concerns:

- `ai_service.py` - AI model integration and logic
- `models.py` - Database schemas and data structures
- `main.py` - API routes and endpoints
- `frontend/components/` - React UI components

## License

MIT License
