#AI Voice Agent

This project is a fully local AI Assistant running on your CPU using Meta's Llama 3.2 model. It has a React frontend and a Python FastAPI backend that processes your voice and handles API requests.

## How to Run the Project

Running this project requires starting three distinct services in **three separate terminal/PowerShell tabs**.

### Step 1: Start the Local LLM (Ollama)
The "brain" of this entire project is powered by Meta's Llama 3.2, which runs completely natively on your machine 
using an engine called Ollama. For the other parts of this app to work, Ollama needs to be actively running in the background.

1. Open a new, completely blank PowerShell terminal.
2. Run the following command to spin up the local AI engine:
```powershell
ollama run llama3.2
```
* **First Time Run:** If you have never run this model before, Ollama will automatically download the ~2.0GB model from the internet.
* **Ready State:** Once it finishes loading, you will see a `>>> Send a message (/? for help)` prompt inside the terminal.
* **What's Happening Under The Hood:** Even though it looks like it's just waiting for you to type, Ollama actually spins up an invisible, built-in API server on `localhost:11434`. This is what allows our Python backend to securely talk to the LLM in real-time!

**Important:** You must leave this terminal window open and running. If you close it, your AI will lose its brain power and the frontend will stop working!

### Step 2: Start the Python Backend API
The backend requires its virtual environment to run the FastAPI server.
1. Open a second PowerShell terminal.
2. Navigate to the backend directory and run `main.py`:
```powershell
cd D:\P\voice_ai_agent\backend
.\venv\Scripts\python.exe main.py
```
*(If successful, you will see it say `Application startup complete.` and Uvicorn running on `0.0.0.0:8000`)*. Leave this terminal open.

### Step 3: Start the React Frontend Web App
The user interface where you type and talk.
1. Open a third PowerShell terminal.
2. Navigate to the frontend directory and start the Vite development server:
```powershell
cd D:\P\voice_ai_agent\frontend
npm run dev
```

### Step 4: Access the AI
Once all three services are running:
1. Open your web browser (Chrome, Edge, Firefox, etc.).
2. Go to `http://localhost:5173/` (or the URL Vite provided in the terminal).
3. Start chatting by typing your message or clicking the microphone icon to talk!

## Quitting the Project
When you're done playing with the project, simply go to each of the three terminal windows and press `CTRL + C` on your keyboard to shut down the servers safely.
