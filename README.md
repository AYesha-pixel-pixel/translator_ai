# translation_agent

An AI Translation Agent built using the [Google Agent Development Kit (ADK)](https://adk.dev/).

The agent features a single root agent (`translation_agent`) powered by Google's Gemini models (defaulting to `gemini-3.8-flash`), designed to translate text accurately across languages while preserving nuance, style, and context.

---

## Project Structure

```
translation_agent/
├── app/
│   ├── agent.py               # Main agent logic and definition (root_agent)
│   ├── fast_api_app.py        # FastAPI backend server
│   └── app_utils/             # Helpers (A2A routes, reasoning engine adapter, services)
├── tests/
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration and E2E tests
├── requirements.txt           # Python package dependencies
├── pyproject.toml             # Project build configuration
├── .env.example               # Environment variables template
└── README.md                  # Project documentation
```

---

## Prerequisites

- **Python 3.11+**
- **uv** (recommended package and project manager): [Installation Guide](https://docs.astral.sh/uv/getting-started/installation/)
- **google-agents-cli** (optional, for CLI tools and playground):
  ```bash
  uv tool install google-agents-cli
  ```
- **Google Cloud SDK** (if using Vertex AI backend): [Installation Guide](https://cloud.google.com/sdk/docs/install)

---

## Installation

### Option 1: Using `uv` (Recommended)

Sync the virtual environment and install all dependencies:
```bash
uv sync
```

Or using `agents-cli`:
```bash
agents-cli install
```

### Option 2: Using standard `pip`

Create and activate a virtual environment, then install from `requirements.txt`:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Configuration

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Configure your environment variables in `.env`:
   - **Model Selection**: Set `MODEL_NAME` (defaults to `gemini-3.8-flash` if omitted).
     ```env
     MODEL_NAME=gemini-3.8-flash
     ```

   - **Credentials Option A — Google Cloud Vertex AI (Default)**:
     ```env
     GOOGLE_GENAI_USE_VERTEXAI=true
     GOOGLE_CLOUD_PROJECT=your-gcp-project-id
     GOOGLE_CLOUD_LOCATION=global
     ```
     Ensure you are authenticated with Google Cloud:
     ```bash
     gcloud auth application-default login
     ```

   - **Credentials Option B — Gemini API via Google AI Studio**:
     Comment out the Vertex AI variables and provide your Gemini API key:
     ```env
     GEMINI_API_KEY=your-gemini-api-key-here
     ```

---

## Running the Agent

### 1. Interactive Testing (agents-cli)

Run a one-off prompt from your terminal:
```bash
agents-cli run "Translate 'Hello, how are you today?' into Spanish and French."
```

Or start the interactive web playground:
```bash
agents-cli playground
```

### 2. Local FastAPI Server

Start the API backend with Uvicorn:
```bash
uv run uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000 --reload
```
Once started, the server exposes:
- Native ADK streaming endpoints: `http://localhost:8000/run_sse`
- A2A protocol endpoint: `http://localhost:8000/a2a/app/`
- Interactive API docs (Swagger): `http://localhost:8000/docs`

### 3. Running Tests

Run unit tests:
```bash
uv run pytest tests/unit
```

Run integration tests:
```bash
uv run pytest tests/integration
```
