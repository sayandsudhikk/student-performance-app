# Student Performance Evaluation System using Cloud-based LLM

This repository contains a complete end-to-end system for a college application titled *Student Performance Evaluation System using Cloud-based LLM*. The project includes a Streamlit frontend and a Flask backend, relying on a local SQLite database and Google Cloud Vertex AI (Gemini) for LLM-based pass/fail prediction.

## Features

- Teacher and student roles with separate workflows
- Upload and parse Excel files with student academic data
- Search and visualize student performance
- Generate evaluations via LLM calls
- Store results with teacher comments and AI recommendations

## Architecture

```
ROOT/
├── backend/          # Flask REST API service
├── ui/               # Streamlit frontend
└── README.md         # This document
```

### Setup Instructions
1. **Backend**
   ```bash
   cd backend
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```
2. **UI**
   ```bash
   cd ../ui
   streamlit run streamlit_app.py
   ```

> Note: Configure Google Cloud credentials and environment variables for Vertex AI integration.
> 
> **Authentication options:**
> 1. Service account with ADC: set `GOOGLE_APPLICATION_CREDENTIALS` to a JSON key file and leave `API_KEY` empty.
> 2. API key from AI Studio: set `API_KEY` in `backend/config/llm_config.py`.
>    * When `USE_GEN_API` is **False** (default), the API key will be used with the
>      Vertex‑AI prediction endpoint; you must also populate `PROJECT_ID` and `MODEL_ID`.
>    * When `USE_GEN_API` is **True**, the system will instead call the
>      *Generative Language API* (`generativelanguage.googleapis.com`) using the simple
>      model name found in Studio (e.g. `gemini-flash-latest`). In this mode you do **not** need
>      a project ID or model ID.



---

The following sections detail project structure, database schema, backend and UI components.