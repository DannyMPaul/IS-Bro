# Idea Shaper

An AI-powered idea refinement assistant that helps transform vague concepts into structured project blueprints through conversational mentorship.

## Features

- **Conversational AI Mentor**: Socratic questioning approach to idea refinement
- **Progressive Idea Development**: Structured conversation flow from initial concept to proposal
- **Interactive Chat Interface**: Clean, intuitive UI with suggestion buttons
- **Real-time AI Processing**: Powered by Llama-3.1-8B-Instruct via Hugging Face

## Tech Stack

### Backend

- **FastAPI**: High-performance Python web framework
- **Hugging Face Transformers**: AI model integration
- **PyTorch**: Deep learning framework
- **Pydantic**: Data validation and settings management

### Frontend

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Lucide React**: Beautiful icon library

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
