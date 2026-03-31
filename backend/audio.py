import os
from faster_whisper import WhisperModel
import edge_tts
import asyncio

# Initialize Faster Whisper Model (CPU optimized)
# The "tiny.en" model is very small and fast on CPUs.
# compute_type="int8" reduces memory usage with minor accuracy loss
print("Starting STT Engine...")
try:
    stt_model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
    print("STT Engine Loaded.")
except Exception as e:
    print(f"Warning: Could not load Whisper model. Error: {e}")
    stt_model = None

def transcribe_audio(file_path: str) -> str:
    """Transcribes an audio file to text using faster-whisper."""
    if not stt_model:
        return "STT Model not initialized properly."
        
    segments, info = stt_model.transcribe(file_path, beam_size=5)
    
    transcription = ""
    for segment in segments:
        transcription += segment.text + " "
        
    return transcription.strip()

async def text_to_speech(text: str, output_path: str = "output.mp3"):
    """Converts text to speech using Microsoft Edge's free TTS service and saves it as an MP3 file."""
    # edge-tts provides very high quality voices for free
    # "en-US-AriaNeural" is a nice female voice. Other good one: "en-US-GuyNeural"
    voice = "en-US-AriaNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path
