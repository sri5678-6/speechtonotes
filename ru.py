from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import whisper
import google.generativeai as genai
from dotenv import load_dotenv
import os
import io
import tempfile
from pydub import AudioSegment
import asyncio

# --- API Key Setup ---
load_dotenv(dotenv_path="api.env")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- FastAPI App ---
app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # change to your frontend URL when deploying
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Model Loading ---
stt_model = None

@app.on_event("startup")
def load_models_on_startup():
    global stt_model
    try:
        print("Loading Whisper model... please wait")
        # Use "base" for speed (switch to "small" if accuracy is more important)
        stt_model = whisper.load_model("base")
        print("✅ Whisper model loaded")
    except Exception as e:
        print(f"❌ Error loading Whisper model: {e}")
        raise RuntimeError("Failed to load Whisper model.")

# --- Summarization ---
def summarize_with_gemini(text: str) -> str:
    try:
        prompt = f"Summarize clearly in simple points:\n\n{text}"
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Summarizer error: {e}")
        return "Summary unavailable, showing full transcription instead."

# --- API Endpoint ---
@app.post("/process-audio/")
async def process_audio(file: UploadFile = File(...)):
    if stt_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")

    try:
        # Read audio
        audio_bytes = await file.read()

        # Convert to wav with pydub
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")

        # Limit audio length (max 60s for hackathon demo)
        if len(audio_segment) > 60_000:
            raise HTTPException(status_code=400, detail="Audio too long. Limit is 60 seconds.")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            audio_segment.export(tmp_wav.name, format="wav")
            wav_file_path = tmp_wav.name

        try:
            # Run Whisper in async thread (non-blocking)
            transcription = await asyncio.to_thread(
                stt_model.transcribe, wav_file_path, fp16=False
            )
            transcribed_text = transcription.get("text", "").strip()

            if not transcribed_text:
                raise HTTPException(status_code=400, detail="No speech detected in audio.")

            # Summarize
            summarized_notes = summarize_with_gemini(transcribed_text)

            return JSONResponse(
                content={
                    "transcription": transcribed_text,
                    "notes": summarized_notes,
                }
            )
        finally:
            # Always clean up temp file
            if os.path.exists(wav_file_path):
                os.remove(wav_file_path)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Server error: {e}")
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
