import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from utils.supabase_client import upload_audio_to_storage
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
    Accepts an audio file upload and saves it to Supabase Storage.
    Returns the public URL of the uploaded file.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # unique filename to prevent overwriting
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'm4a'
    unique_filename = f"{uuid.uuid4()}.{ext}"
    
    try:
        file_bytes = await file.read()
        public_url = upload_audio_to_storage(file_bytes, unique_filename, content_type=file.content_type or "audio/mp4")
        return {"status": "success", "url": public_url, "filename": unique_filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
