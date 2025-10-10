

# Voice Agent Tool 🎯

A full-stack voice agent system with a FastAPI backend and a modern React frontend. Designed for managing driver calls, integrating with Supabase, and providing a seamless dashboard experience.

---

## � Contents

- [Backend (FastAPI)](#backend-fastapi)
- [Frontend (React + Vite)](#frontend-react--vite)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quickstart](#quickstart)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Environment Variables](#environment-variables)



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
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
RETELL_API_KEY=your-retell-api-key (optional)
LOG_LEVEL=INFO
HOST=localhost
PORT=8000
RELOAD=True
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

> **Note:** Replace placeholder values with your actual credentials.

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

### Getting Supabase Credentials

1. Go to [Supabase Dashboard](https://app.supabase.com/)
2. Select your project or create a new one
3. Go to **Settings** → **API**
4. Copy the **Project URL** and **anon/public key**
5. Add them to your `.env` file

### Optional Configuration

You can customize additional settings in `.env`:

```env
# Server Configuration
HOST=localhost
PORT=8000
RELOAD=True

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
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


**Happy coding!** 💻✨