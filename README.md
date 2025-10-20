
# 🎯 AI Voice Agent Tool - PIPECAT Edition

A comprehensive logistics voice agent system built with **PIPECAT framework** for self-hosted, real-time voice interactions. This tool enables logistics dispatchers to conduct professional voice calls with truck drivers for status updates and emergency handling.

## 🚀 Features

### Core Functionality
- **PIPECAT Voice Framework**: Self-hosted voice agent with real-time processing
- **Agent Configuration UI**: Intuitive interface for conversation prompts and scenarios
- **Real-time Voice Calls**: Web-based and phone call capabilities
- **Live Transcription**: Real-time speech-to-text with Web Speech API
- **Analytics Dashboard**: Comprehensive call metrics and trends
- **Emergency Detection**: Automatic emergency protocol handling

### Advanced Voice Features
- **Live Speech Recognition**: Browser-based voice input processing
- **Intelligent Responses**: Context-aware AI dispatcher conversations
- **Microphone Controls**: Mute/unmute with visual feedback
- **Call Duration Tracking**: Real-time call timing
- **Professional Voice Scenarios**: Logistics-specific conversation templates

## 🏗️ Technology Stack

- **Voice Engine**: PIPECAT (Self-hosted voice agent framework)
- **Frontend**: React 18 + TypeScript + Tailwind CSS + Vite
- **Backend**: FastAPI + Python 3.10+
- **Database**: Supabase (PostgreSQL)
- **Real-time Processing**: WebSocket connections
- **Speech Recognition**: Web Speech API
- **Analytics**: RTVI events tracking

## 📁 Project Structure

```
voice-agent-tool/
├── backend/                    # FastAPI Backend
│   ├── main.py                # Application entry point
│   ├── requirements.txt       # Python dependencies
│   ├── database_setup.sql     # Database schema
│   └── app/
│       ├── core/              # Configuration & settings
│       ├── database/          # Supabase integration
│       ├── models/            # Pydantic schemas
│       ├── pipecat/           # PIPECAT voice service
│       ├── routes/            # API endpoints
│       │   ├── agent_routes.py
│       │   ├── call_routes.py
│       │   ├── analytics_routes.py
│       │   └── webhook_routes.py (deprecated)
│       └── services/          # Business logic
│
├── frontend/                  # React Frontend  
│   ├── src/
│   │   ├── components/       # UI components
│   │   │   ├── AgentConfiguration.tsx
│   │   │   ├── CallInterface.tsx
│   │   │   ├── CallResults.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── analytics/    # Analytics components
│   │   │   └── ui/           # Reusable UI components
│   │   ├── hooks/            # Custom React hooks
│   │   │   ├── usePipecat.ts # PIPECAT integration
│   │   │   └── useRetell.ts  # Legacy (deprecated)
│   │   ├── types/            # TypeScript definitions
│   │   └── utils/            # API client & utilities
│   ├── package.json
│   └── vite.config.ts
│
└── README.md                 # This file
```

## 🔧 Prerequisites

- **Python 3.10+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **Supabase Account** - [Sign up](https://supabase.com/)
- **OpenAI API Key** - [Get API Key](https://platform.openai.com/api-keys)

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/sampson169/AI-Voice-Agent-Tool.git
cd AI-Voice-Agent-Tool
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### 3. Database Setup

1. **Create Supabase Project** at [supabase.com](https://supabase.com)
2. **Copy credentials** from Settings → API
3. **Run database schema** in Supabase SQL Editor:
   ```sql
   -- Copy and paste entire contents of backend/database_setup.sql
   ```

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies  
npm install

# Start development server
npm run dev
```

### 5. Start Backend

```bash
cd ../backend

# Start FastAPI server
python main.py
```

## ⚙️ Configuration

### Backend Environment (.env)

```env
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_api_key

# Optional PIPECAT Services
CARTESIA_API_KEY=your_cartesia_key  # Advanced TTS
DEEPGRAM_API_KEY=your_deepgram_key  # Advanced STT

# Server Settings
HOST=localhost
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174
```

### Frontend Configuration

The frontend automatically connects to `http://localhost:8000`. To change the backend URL, update `src/utils/config.ts`.

## 🎯 Key Features

### PIPECAT Voice Integration
- **Self-hosted Voice Agent**: No dependency on external voice services
- **Real-time Processing**: Low-latency voice interactions
- **Web Speech API**: Browser-based speech recognition
- **Professional Conversations**: Logistics-specific scenarios

### Analytics Dashboard
- **Call Metrics**: Duration, tokens, interruptions
- **Outcome Tracking**: Status updates, emergencies, confirmations
- **Trends Analysis**: Daily/weekly performance charts
- **RTVI Events**: Detailed interaction tracking

### Emergency Handling
- **Automatic Detection**: Emergency phrase recognition
- **Priority Response**: Safety-first conversation flow
- **Escalation Protocol**: Human dispatcher handoff
- **Location Tracking**: Highway/mile marker identification

## 📊 API Documentation

Once running, access interactive API docs at:
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API status |
| `POST` | `/api/calls/start` | Start PIPECAT call |
| `GET` | `/api/calls/{id}/result` | Get call results |
| `GET` | `/api/analytics/dashboard` | Dashboard metrics |
| `GET` | `/api/analytics/trends` | Analytics trends |
| `GET` | `/api/agents/` | List agent configs |

## 🔧 Development

### Adding New Features

1. **Models**: Define schemas in `app/models/schemas.py`
2. **Database**: Add operations to `app/database/supabase.py`
3. **Services**: Implement logic in `app/services/`
4. **Routes**: Create endpoints in `app/routes/`
5. **Frontend**: Add components in `src/components/`

### PIPECAT Integration

The PIPECAT service (`app/pipecat/pipecat_service.py`) handles:
- Voice call initialization
- Speech recognition setup
- AI response generation
- Call session management

### Analytics System

Analytics data flows through:
1. **RTVI Events**: Real-time interaction tracking
2. **Call Metrics**: Aggregated call statistics
3. **Daily Analytics**: Computed daily summaries
4. **Frontend Charts**: Real-time dashboard updates

## 🧪 Testing

### Backend Testing
```bash
cd backend

# Test API endpoints
curl -X GET http://localhost:8000/
curl -X GET http://localhost:8000/api/analytics/dashboard?days=30

# Health check
curl -X GET http://localhost:8000/api/analytics/health
```

### Frontend Testing
```bash
cd frontend

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🚨 Troubleshooting

### Common Issues

**Backend won't start**
- Check Python version (3.10+ required)
- Verify virtual environment is activated
- Ensure all dependencies are installed

**Database connection failed**
- Verify Supabase credentials in `.env`
- Check internet connection
- Ensure database schema is installed

**Voice not working**
- Allow microphone access in browser
- Check CORS settings in backend
- Verify OpenAI API key is valid

**Analytics not loading**
- Ensure database tables exist (run `database_setup.sql`)
- Check backend logs for errors
- Verify API endpoints are accessible

### Getting Help

1. Check the **terminal logs** for error details
2. Visit `/docs` for API documentation
3. Test `/api/analytics/health` for service status
4. Review browser console for frontend errors

## 🔄 Migration from Retell AI

This project has been migrated from Retell AI to PIPECAT for better control and self-hosting capabilities:

### What Changed
- ✅ **Voice Engine**: Retell AI → PIPECAT
- ✅ **Hosting**: External → Self-hosted
- ✅ **Analytics**: Enhanced RTVI tracking
- ✅ **Real-time**: Web Speech API integration
- ✅ **Database**: Extended schema for analytics

### Deprecated Components
- `useRetell.ts` hook (replaced by `usePipecat.ts`)
- `webhook_routes.py` (PIPECAT uses direct integration)
- External voice service dependencies

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**🎉 Happy Voice Dispatching!** 

Built with ❤️ using PIPECAT, React, and FastAPI

## 🚀 Features

### Core Functionality
- **Agent Configuration UI**: Intuitive interface to define conversation prompts and voice settings
- **Call Triggering System**: Ability to initiate both web and phone calls with driver context
- **Real-time Call Management**: Live call monitoring with transcript display
- **Structured Data Extraction**: Automatic extraction of key information into structured summaries
- **Emergency Protocol Handling**: Immediate detection and response to emergency situations

### Logistics-Specific Scenarios

#### Scenario 1: End-to-End Driver Check-in
- Dynamic conversation flow that adapts based on driver responses
- Handles three main driver states: Driving, Arrived, Delayed
- Extracts structured data: location, ETA, delay reasons, unloading status
- Professional conversation management with natural backchanneling

#### Scenario 2: Emergency Protocol
- Immediate emergency detection using trigger phrases
- Priority-based response: Safety → Location → Details → Escalation
- Structured emergency data collection
- Automatic escalation to human dispatchers

### Advanced Voice Configuration
- **Optimal Voice Settings**: Configured for human-like interactions
- **Backchanneling**: Natural "uh-huh", "okay" responses
- **Filler Words**: Natural speech patterns
- **Interruption Sensitivity**: Configurable response to speaker interruptions
- **Dynamic Response Generation**: Context-aware conversation management

## 🛠 Technology Stack

- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python
- **Database**: Supabase (PostgreSQL)
- **Voice System**: Retell AI
- **Deployment**: Ready for production deployment

## 📋 Project Requirements Fulfillment

### Core Requirements ✅
- ✅ Agent Configuration UI with prompt and logic definition
- ✅ Call triggering with driver name, phone number, and load number inputs
- ✅ Structured results display with key-value pairs alongside full transcripts
- ✅ Backend webhook handling for real-time conversation management
- ✅ Post-processing for structured data extraction

### Logistics Scenarios ✅

#### Task A: Optimal Voice Configuration ✅
- ✅ Implemented backchanneling, filler words, and interruption sensitivity
- ✅ Human-like conversation patterns with natural speech flow
- ✅ Professional yet friendly tone throughout interactions

#### Scenario 1: Driver Check-in ✅
- ✅ End-to-end conversation handling with dynamic branching
- ✅ Open-ended status inquiry with adaptive follow-up questions
- ✅ Structured data extraction for all required fields:
  - `call_outcome`: "In-Transit Update" OR "Arrival Confirmation"
  - `driver_status`: "Driving" OR "Delayed" OR "Arrived" OR "Unloading"
  - `current_location`: Highway, mile markers, city information
  - `eta`: Estimated arrival times
  - `delay_reason`: Traffic, Weather, Mechanical, etc.
  - `unloading_status`: Dock assignments, door numbers, detention
  - `pod_reminder_acknowledged`: Proof of delivery reminders

#### Scenario 2: Emergency Protocol ✅
- ✅ Immediate emergency detection and protocol switch
- ✅ Priority-based information gathering (Safety → Location → Details)
- ✅ Structured emergency data extraction:
  - `call_outcome`: "Emergency Escalation"
  - `emergency_type`: "Accident" OR "Breakdown" OR "Medical" OR "Other"
  - `safety_status`: Confirmed safety information
  - `injury_status`: Injury assessment
  - `emergency_location`: Exact highway position
  - `load_secure`: Cargo security status
  - `escalation_status`: "Connected to Human Dispatcher"

#### Task B: Dynamic Response Handling ✅
- ✅ **Uncooperative Driver Handling**: Probes 2-3 times, then graceful call termination
- ✅ **Noisy Environment Management**: Asks for repetition with limited attempts
- ✅ **Conflicting Information**: Non-confrontational handling of discrepancies

## 🏗 Architecture & Design Choices

### Backend Architecture
```
backend/
├── app/
│   ├── core/           # Configuration and settings
│   ├── database/       # Supabase client and database operations
│   ├── models/         # Pydantic schemas and data models
│   ├── routes/         # API endpoints (agents, calls, webhooks)
│   └── services/       # Business logic (Retell integration, prompt templates)
├── main.py            # FastAPI application entry point
└── database_setup.sql # Database schema and initial data
```

### Frontend Architecture
```
frontend/src/
├── components/        # React components
│   ├── AgentConfiguration.tsx  # Agent setup and scenario selection
│   ├── CallInterface.tsx       # Call management and live monitoring
│   └── CallResults.tsx         # Results display and data analysis
├── hooks/             # Custom React hooks (Retell integration)
├── types/             # TypeScript interfaces
└── utils/             # API client and utilities
```

### Key Design Decisions

#### 1. Modular Prompt Templates
Created `LogisticsPromptTemplates` service with predefined scenarios:
- **Driver Check-in**: Optimized for routine status updates
- **Emergency Protocol**: Specialized for crisis response
- **General**: Hybrid approach handling both scenarios

#### 2. Enhanced Conversation State Management
Implemented sophisticated state tracking:
- **Phase-based progression**: greeting → inquiry → follow-up → wrap-up
- **Emergency state override**: Immediate protocol switch when triggered
- **Clarification handling**: Manages unclear responses with retry logic
- **Uncooperative driver detection**: Identifies and handles minimal responses

#### 3. Advanced Data Extraction
Built comprehensive extraction logic:
- **Location parsing**: Supports highways, mile markers, cities, exits
- **Time extraction**: ETA patterns including relative and absolute times
- **Emergency categorization**: Automatic classification of emergency types
- **Confidence scoring**: Emergency detection with confidence levels

#### 4. Human-like Voice Configuration
Optimized settings for natural conversations:
```python
OPTIMAL_VOICE_SETTINGS = {
    "voice_id": "11labs-Adrian",
    "speed": 1.0,
    "temperature": 0.7,
    "backchanneling": True,
    "filler_words": True,
    "interruption_sensitivity": "medium",
    "response_delay": 0.3,
    "enable_interruption": True
}
```
---

## ✨ Features

- 🚀 **FastAPI Backend** - Modern, fast web framework
- 🗄️ **Supabase Integration** - Real-time database operations
- 📞 **Call Management** - Start and track voice calls
- 🔗 **Webhook Support** - Retell AI integration
- 🏗️ **Modular Architecture** - Clean, scalable code structure
- 📚 **Auto-generated API Docs** - Interactive documentation
- 🔄 **Auto-reload** - Development-friendly hot reload
- ✅ **Health Checks** - Service status monitoring
- ⚡ **React Frontend** - Fast, modern UI with Vite, TypeScript, and Tailwind CSS


## ✨ Features

- � **FastAPI Backend** - Modern, fast web framework
- 🗄️ **Supabase Integration** - Real-time database operations
- 📞 **Call Management** - Start and track voice calls
- 🔗 **Webhook Support** - Retell AI integration
- 🏗️ **Modular Architecture** - Clean, scalable code structure
- 📚 **Auto-generated API Docs** - Interactive documentation
- 🔄 **Auto-reload** - Development-friendly hot reload
- ✅ **Health Checks** - Service status monitoring
- ⚡ **React Frontend** - Fast, modern UI with Vite, TypeScript, and Tailwind CSS



## �📁 Project Structure

```
voice-agent-tool/
├── backend/         # FastAPI backend
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│   ├── README.md
│   └── app/
│       ├── core/
│       ├── database/
│       ├── models/
│       ├── services/
│       └── routes/
├── frontend/        # React + Vite frontend
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── README.md
└── README.md        # Global documentation (this file)
```



## 🔧 Prerequisites

- **Python 3.10+** (for backend) - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** (for frontend) - [Download Node.js](https://nodejs.org/)
- **npm** (comes with Node.js)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Supabase Account** - [Sign up for Supabase](https://supabase.com/)



## 🚀 Quickstart

### 1. Clone the Repository
```
git clone https://github.com/sampson169/AI-Voice-Agent-Tool.git
```
---


# Voice Agent Tool

A full-stack solution for managing driver calls, featuring a FastAPI backend and a React (Vite + TypeScript) frontend, with Supabase integration and a modern dashboard UI.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

Voice Agent Tool streamlines and automates driver call management for logistics and transportation companies. It leverages modern web technologies for a robust, scalable, and user-friendly experience.

---

## Features

- **FastAPI Backend**: High-performance Python API server
- **Supabase Integration**: Real-time database operations
- **Call Management**: Start, track, and review voice calls
- **Webhook Support**: Integrate with Retell AI and other services
- **Modular Architecture**: Clean, scalable codebase
- **Auto-generated API Docs**: Interactive Swagger UI
- **Hot Reload**: Fast development workflow
- **Health Checks**: Service status endpoints
- **React Frontend**: Modern UI with Vite, TypeScript, and Tailwind CSS

---

## Project Structure

```
voice-agent-tool/
├── backend/         # FastAPI backend
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── core/
│       ├── database/
│       ├── models/
│       ├── services/
│       └── routes/
├── frontend/        # React + Vite frontend
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
└── README.md        # Global documentation (this file)
```

---

## Prerequisites

- Python 3.10+ (for backend)
- Node.js 18+ (for frontend)
- npm (comes with Node.js)
- Git
- Supabase Account ([Sign up](https://supabase.com/))

---

## Backend Setup

1. Open a terminal and navigate to the backend directory:
  ```bash
  cd backend
  ```
2. Create a virtual environment:
  ```bash
  python -m venv venv
  ```
3. Activate the virtual environment:
  - **Windows:**
    ```cmd
    venv\Scripts\activate
    ```
  - **macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```
4. Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
5. Configure environment variables:
  - Copy `.env.example` to `.env` and fill in your Supabase and other credentials.
6. Run the backend server:
  ```bash
  python main.py
  ```
  - The backend will be available at [http://localhost:8000](http://localhost:8000)

---

## Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
  ```bash
  cd frontend
  ```
2. Install dependencies:
  ```bash
  npm install
  ```
3. Start the development server:
  ```bash
  npm run dev
  ```
  - The frontend will be available at [http://localhost:3000](http://localhost:3000)

---

## Configuration

### Backend (.env)

Create a `.env` file in the `backend/` directory with the following variables:

```env
PORT=8000
SUPABASE_URL=
SUPABASE_KEY=
RETELL_API_KEY=
RETELL_AGENT_ID=
RETELL_WEBHOOK_URL=https://0ae6ed66482a.ngrok-free.app/api/webhook/retell
```

> **Note:** Replace placeholder values with your actual credentials.

---

## 🎯 Retell AI Agent Creation & Ngrok Setup

### Setting Up Retell AI Agent

1. **Create a Retell AI Account**
   - Visit [Retell AI Dashboard](https://beta.retellai.com/)
   - Sign up or log in to your account

2. **Create a New Agent**
   - Go to the "Agents" section in your dashboard
   - Click "Create Agent"
   - Configure your agent with the following settings:

   ```json
   {
     "agent_name": "Logistics Dispatcher Agent",
     "voice_id": "11labs-Adrian",
     "response_delay": 600,
     "llm_websocket_url": "wss://api.openai.com/v1/realtime",
     "begin_message": "Hello! This is your logistics dispatcher. I'm calling to check on your current status and location. How are things going on your route today?",
     "general_prompt": "You are a professional logistics dispatcher calling to check on a truck driver...",
     "general_tools": [],
     "states": [],
     "last_modification_timestamp": 1635724800000,
     "voice_temperature": 1,
     "voice_speed": 1,
     "volume": 1,
     "responsiveness": 1,
     "interruption_sensitivity": 1,
     "enable_backchannel": true,
     "backchannel_frequency": 0.9,
     "backchannel_words": ["yeah", "uh-huh", "gotcha", "I see", "okay"],
     "reminder_trigger_ms": 10000,
     "reminder_max_count": 2,
     "ambient_sound": "office",
     "language": "en-US",
     "webhook_url": "YOUR_NGROK_URL/api/webhook/retell",
     "boosted_keywords": ["driver", "truck", "delivery", "location", "ETA", "emergency"],
     "enable_transcription_formatting": true,
     "opt_out_sensitive_data_storage": false,
     "pronunciation_dictionary": [],
     "normalize_for_speech": true,
     "end_call_after_silence_ms": 30000,
     "max_call_duration_ms": 1800000,
     "from_number": "+1234567890",
     "dynamic_variables": [],
     "analysis_schema": {},
     "client_messages": [],
     "tool_call_strict_mode": false,
     "metadata": {}
   }
   ```

3. **Get Your Agent ID**
   - After creating the agent, copy the Agent ID
   - Add it to your `.env` file as `RETELL_AGENT_ID`

### Setting Up Ngrok for Backend Webhooks

Ngrok creates a secure tunnel to your local backend, allowing Retell AI to send webhooks to your development environment.

1. **Install Ngrok**
   ```bash
   # Download from https://ngrok.com/download
   # Or install via package manager:
   
   # Windows (Chocolatey)
   choco install ngrok
   
   # macOS (Homebrew)
   brew install ngrok/ngrok/ngrok
   
   # Linux (Snap)
   sudo snap install ngrok
   ```

2. **Sign Up and Get Auth Token**
   - Create account at [ngrok.com](https://ngrok.com/)
   - Get your auth token from the dashboard
   - Configure ngrok:
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

3. **Start Ngrok Tunnel**
   ```bash
   # Make sure your backend is running on port 8000
   ngrok http 8000
   ```

   You'll see output like:
   ```
   Session Status                online
   Account                       your-email@example.com
   Version                       3.0.0
   Region                        United States (us)
   Forwarding                    https://abc123def.ngrok-free.app -> http://localhost:8000
   ```

4. **Copy the Ngrok URL**
   - Copy the `https://abc123def.ngrok-free.app` URL
   - This is your public webhook URL

### Configuring Agent with Ngrok URL

1. **Update Environment Variables**
   Add the ngrok URL to your `.env` file:
   ```env
   RETELL_WEBHOOK_URL=https://abc123def.ngrok-free.app/api/webhook/retell
   ```

2. **Update Retell AI Agent Configuration**
   - Go back to your Retell AI dashboard
   - Edit your agent
   - Update the webhook URL field:
   ```
   Webhook URL: https://abc123def.ngrok-free.app/api/webhook/retell
   ```

3. **Test the Configuration**
   - Start your backend: `python main.py`
   - Start ngrok: `ngrok http 8000`
   - Make a test call through your frontend
   - Check ngrok logs to see incoming webhook requests

### Important Notes

- **Ngrok URL Changes**: Free ngrok URLs change each time you restart ngrok. For persistent URLs, consider upgrading to ngrok Pro
- **HTTPS Required**: Retell AI requires HTTPS webhooks, which ngrok provides automatically
- **Firewall**: Ensure your firewall allows ngrok connections
- **Testing**: Use ngrok's web interface at `http://127.0.0.1:4040` to inspect webhook requests

### Webhook Testing

You can test webhook delivery using the ngrok web interface:

1. Open `http://127.0.0.1:4040` in your browser
2. View incoming webhook requests in real-time
3. Inspect request headers, body, and response codes
4. Debug webhook issues by examining the detailed logs

---

## API Documentation

Once the backend is running, access the interactive API docs at:

- [http://localhost:8000/docs](http://localhost:8000/docs)

### Example Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/`      | Root information |
| GET    | `/docs`  | Swagger UI |
| GET    | `/api/v1/health/` | Health check |
| POST   | `/api/v1/calls/start` | Start a new call |
| GET    | `/api/v1/calls/results/{call_id}` | Get call results |
| POST   | `/api/v1/webhook/retell` | Retell AI webhook |

---

## Troubleshooting

**Virtual Environment Not Activated**
> Error: `ModuleNotFoundError: No module named 'fastapi'`
- Solution: Activate your virtual environment and install dependencies.

**Missing Environment Variables**
> Error: `AttributeError: 'NoneType' object has no attribute...`
- Solution: Check your `.env` file for correct values.

**Port Already in Use**
> Error: `[Errno 48] Address already in use`
- Solution: Kill the process using the port or use a different port.

**Supabase Connection Failed**
> Error: `❌ Supabase connection failed`
- Solution: Verify your Supabase URL and API key, check your internet connection.

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

---

## License

This project is licensed under the MIT License.

---

**Happy coding!** 🚀
# Configure environment variables (.env)
# (see below for details)

# Run the backend
python main.py
```

The backend will be available at [http://localhost:8000](http://localhost:8000)

---

## Frontend (React + Vite)

### Setup & Run

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000)

---



## ⚙️ Backend Configuration

### Getting Required API Keys

#### 1. Supabase Credentials
1. Go to [Supabase Dashboard](https://app.supabase.com/)
2. Select your project or create a new one
3. Go to **Settings** → **API**
4. Copy the **Project URL** and **anon/public key**
5. Add them to your `.env` file

#### 2. OpenAI API Key (Required for PIPECAT)
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Click **Create new secret key**
5. Copy the key and add it to your `.env` file as `OPENAI_API_KEY`

> **Note:** OpenAI API key is required for the PIPECAT voice agent to function properly.

### Optional Configuration

You can customize additional settings in `.env`:

```env
# Server Configuration
HOST=localhost
PORT=8000
RELOAD=True

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Optional PIPECAT Services
CARTESIA_API_KEY=your_cartesia_api_key_here  # For advanced TTS
DEEPGRAM_API_KEY=your_deepgram_api_key_here  # For advanced STT
```



## 🏃‍♂️ Running the Backend

### Step 1: Activate Virtual Environment (if not already activated)

**Windows:**
```cmd
venv\\Scripts\\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 2: Start the Application

```bash
# Make sure you're in the backend directory
python main.py
```

You should see output similar to:

```
INFO:     Will watch for changes in these directories: ['C:\\path\\to\\backend']
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
INFO:main:🚀 Starting Voice Agent Tool...
INFO:httpx:HTTP Request: GET https://your-project.supabase.co/rest/v1/ "HTTP/1.1 200 OK"
INFO:app.database.supabase:✅ Supabase is Connected
INFO:     Application startup complete.
```

### Step 3: Verify Installation

Open your browser and navigate to:

- **Application:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/v1/health



## 📚 API Documentation (Backend)

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root information |
| `GET` | `/docs` | Interactive API documentation |
| `GET` | `/api/v1/health/` | Health check with service status |
| `POST` | `/api/v1/calls/start` | Start a new call |
| `GET` | `/api/v1/calls/results/{call_id}` | Get call results |
| `POST` | `/api/v1/webhook/retell` | Retell AI webhook |

### Example API Calls

**Start a Call:**
```bash
curl -X POST "http://localhost:8000/api/v1/calls/start" \\
  -H "Content-Type: application/json" \\
  -d '{
    "phone_number": "+1234567890",
    "driver_name": "John Doe",
    "load_number": "LOAD123"
  }'
```

**Health Check:**
```bash
curl -X GET "http://localhost:8000/api/v1/health/"
```



## 🛠️ Backend Development

### Running in Development Mode

The application automatically runs in development mode with:
- **Auto-reload** on file changes
- **Debug logging**
- **CORS enabled** for frontend development

### Adding New Features

1. **Models:** Add new Pydantic models to `app/models/schemas.py`
2. **Database:** Add operations to `app/database/supabase.py`
3. **Services:** Add business logic to `app/services/`
4. **APIs:** Add new endpoints to `app/api/`
5. **Update:** Include new routers in `app/api/main.py`

### Code Structure Guidelines

- Follow **FastAPI best practices**
- Use **type hints** everywhere
- Keep **business logic** in services layer
- Use **Pydantic models** for validation
- Write **descriptive docstrings**



## 🔍 Backend Troubleshooting

### Common Issues

**1. Virtual Environment Not Activated**
```
Error: ModuleNotFoundError: No module named 'fastapi'
Error: ModuleNotFoundError: No module named 'httpx'
```
**Solution:** Make sure your virtual environment is activated and dependencies are installed:
```bash
# Windows
venv\\Scripts\\activate
pip install -r requirements.txt

# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```

**2. Missing Environment Variables**
```
Error: AttributeError: 'NoneType' object has no attribute...
```
**Solution:** Check your `.env` file has the correct Supabase credentials.

**3. Port Already in Use**
```
Error: [Errno 48] Address already in use
```
**Solution:** Kill the existing process or use a different port:
```bash
# Kill process on port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port 8000 (macOS/Linux)
lsof -ti:8000 | xargs kill -9
```

**4. Supabase Connection Failed**
```
INFO:app.database.supabase:❌ Supabase connection failed
```
**Solution:** 
- Verify your Supabase URL and API key in `.env`
- Check your internet connection
- Ensure your Supabase project is active

### Getting Help

1. Check the **logs** in the terminal for detailed error messages
2. Visit **http://localhost:8000/docs** for interactive API documentation
3. Check **http://localhost:8000/api/v1/health** for service status
4. Ensure all **dependencies** are installed correctly

### Development Tips

- Use `Ctrl+C` to stop the server
- The server auto-reloads when you make code changes
- Check the terminal output for detailed logging
- Use the `/docs` endpoint to test APIs interactively



## 📝 Backend Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Your Supabase project URL | `https://abc123.supabase.co` |
| `SUPABASE_KEY` | Your Supabase anon/public key | `eyJhbGciOiJIUzI1NiI...` |
| `RETELL_API_KEY` | Retell AI API key (optional) | `your_retell_key_here` |
| `LOG_LEVEL` | Logging level | `INFO` (default) |
| `HOST` | Server host | `localhost` (default) |
| `PORT` | Server port | `8000` (default) |

---

## 🎉 Success!

If you see **"✅ Supabase is Connected"** in your terminal logs, you're all set! 


Your backend is now running at **http://localhost:8000** 🚀

---


---

## 📖 Frontend Documentation

### Features
- ⚡ Fast, modern UI with React 19 and Vite
- 🎨 Styled with Tailwind CSS
- 🔗 Connects to FastAPI backend
- 📞 Call interface and results dashboard
- 🔒 TypeScript for type safety
- 🔄 API integration via Axios

### Project Structure
```
frontend/
├── public/                # Static assets
├── src/
│   ├── components/        # UI components
│   ├── hooks/             # Custom React hooks
│   ├── types/             # TypeScript types
│   ├── utils/             # Utility functions (API, etc.)
│   ├── App.tsx            # Main app component
│   ├── main.tsx           # Entry point
│   └── index.css          # Tailwind CSS
├── package.json           # Project metadata & scripts
├── tailwind.config.js     # Tailwind config
├── vite.config.ts         # Vite config
└── tsconfig.json          # TypeScript config
```

### Prerequisites
- **Node.js 18+** ([Download Node.js](https://nodejs.org/))
- **npm** (comes with Node.js)

### Installation
```bash
cd frontend
npm install
```

### Running the App
```bash
npm run dev
```
- The app will be available at [http://localhost:3000](http://localhost:3000)
- Make sure the backend is running at [http://localhost:8000](http://localhost:8000)

### Available Scripts
- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Lint code with ESLint

### Development
- Edit components in `src/components/`
- API calls are managed in `src/utils/api.ts`
- Update types in `src/types/`
- Use hooks from `src/hooks/`
- UI is styled with Tailwind CSS (`index.css`)

### Environment Variables
- By default, API requests are sent to `http://localhost:8000` (see `src/utils/api.ts`)
- To change the backend URL, update the API base URL in `api.ts`

---

---