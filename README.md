# Idea Shaper

An AI-powered idea refinement assistant that helps transform vague concepts into structured project blueprints through conversational mentorship.

## Features

- **🧠 Conversational AI Mentor**: Socratic questioning approach to idea refinement
- **📈 Progressive Idea Development**: Structured conversation flow from initial concept to proposal
- **💬 Professional Chat Interface**: Modern, vibrant UI with dynamic timestamps and message bubbles
- **⚡ Real-time AI Processing**: Powered by Gemini 1.5 Flash with multi-AI integration
- **🔍 Market Research Integration**: Automated competitor analysis and industry insights
- **🗺️ Visual Idea Mapping**: Interactive concept visualization with relationship detection
- **📊 Advanced Analytics**: Comprehensive dashboard with user behavior tracking
- **🎨 Vibrant Design**: Gradient backgrounds, smooth animations, and professional styling

## Tech Stack

### Backend

- **FastAPI**: High-performance Python web framework with async support
- **Multi-AI Integration**: Gemini, OpenAI GPT-4, and Anthropic Claude support
- **SQLAlchemy**: Modern ORM with SQLite database
- **Market Research APIs**: News API, SERP API, Crunchbase integration
- **NetworkX**: Graph-based visual mapping and relationship detection
- **Pydantic**: Data validation and settings management

### Frontend

- **Next.js 14**: React framework with App Router and SSR
- **TypeScript**: Type-safe development with modern ES features
- **Tailwind CSS**: Utility-first styling with custom animations
- **Lucide React**: Beautiful, consistent icon library
- **Date-fns**: Modern date formatting and manipulation
- **Gradient Design**: Vibrant colors, smooth animations, and professional UI

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- CUDA-compatible GPU (recommended for AI model)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The web interface will be available at `http://localhost:3000`

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

1. Start both backend and frontend servers
2. Open `http://localhost:3000` in your browser
3. Share your idea in the chat interface
4. Follow Big Brother's guidance through the refinement process
5. Receive a structured project proposal

## API Endpoints

- `POST /api/chat` - Send message to AI mentor
- `GET /api/conversation/{session_id}` - Retrieve conversation history
- `POST /api/proposal/{session_id}` - Generate structured proposal
- `GET /health` - Health check

## Development

The application follows a clean architecture with separate concerns:

- AI logic in `ai_service.py`
- Data models in `models.py`
- API routes in `main.py`
- React components in `frontend/components/`

## License

MIT License
