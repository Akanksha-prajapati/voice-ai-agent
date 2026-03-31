from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import shutil
import os
import tempfile

from agent import run_agent
from audio import transcribe_audio, text_to_speech

app = FastAPI(title="Voice AI Agent API")

# Add CORS to allow the frontend React app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Voice AI Agent API is running!"}

@app.post("/api/chat")
async def chat_endpoint(message: str = Form(...)):
    """Simple text-in, text-out endpoint using the LangChain Agent"""
    try:
        response_text = run_agent(message)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice-chat")
async def voice_chat_endpoint(audio: UploadFile = File(...)):
    """Accepts an audio file upload, transcribes it, runs the agent, and returns an mp3 voice response."""
    try:
        # 1. Save uploaded WebM audio to a temporary file
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
        shutil.copyfileobj(audio.file, temp_input)
        temp_input.close() # Ensure file is closed so STT engine can read it on Windows
        
        # 2. Transcribe Audio (STT)
        user_text = transcribe_audio(temp_input.name)
        os.unlink(temp_input.name) # cleanup input file
        
        if not user_text or user_text.strip() == "":
             raise HTTPException(status_code=400, detail="Could not transcribe audio.")
             
        # 3. Get Agent Response
        agent_response = run_agent(user_text)
        
        # 4. Synthesize AI Voice (TTS)
        temp_dir = tempfile.gettempdir()
        output_mp3_path = os.path.join(temp_dir, f"response_{os.urandom(4).hex()}.mp3")
        
        # We need to await the edge-tts async function here
        await text_to_speech(agent_response, output_mp3_path)
        
        # 5. Return the MP3 file directly
        return FileResponse(
            path=output_mp3_path, 
            media_type="audio/mpeg", 
            filename="response.mp3"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
