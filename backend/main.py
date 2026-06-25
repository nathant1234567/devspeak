import os
import uuid
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from utils.supabase_client import upload_audio_to_storage
from utils.gemini_client import evaluate_interview_audio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="DevSpeak API",
    description="Backend for the DevSpeak mobile application",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # reminder: restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the DevSpeak API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Accepts an audio file upload, saves it to Supabase Storage,
    and evaluates the audio natively using Google Gemini 1.5 Flash.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Generate a unique filename to prevent overwriting
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'm4a'
    unique_filename = f"{uuid.uuid4()}.{ext}"
    
    try:
        # Read the file bytes for Supabase
        file_bytes = await file.read()
        public_url = upload_audio_to_storage(file_bytes, unique_filename, content_type=file.content_type or "audio/mp4")
        
        # OpenAI Whisper requires a physical file, so we save it to a temporary directory
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_audio:
            temp_audio.write(file_bytes)
            temp_audio_path = temp_audio.name
            
        # Call Gemini Integration directly with the audio file
        feedback = evaluate_interview_audio(temp_audio_path)
        
        # Clean up the temporary file from the server
        os.remove(temp_audio_path)
        
        return {
            "status": "success", 
            "url": public_url, 
            "feedback": feedback
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
