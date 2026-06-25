import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
# using the service role key ensures the backend has full permissions to bypass Row Level Security 
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

def get_supabase_client() -> Client:
    """Initialize and return the Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase credentials not found in environment variables. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_audio_to_storage(file_bytes: bytes, filename: str, content_type: str = "audio/mp4") -> str:
    """
    Uploads audio bytes to the 'interviews' Supabase storage bucket and returns the public URL.
    """
    supabase = get_supabase_client()
    bucket_name = "interviews"
    
    # The path where the file will be saved in the bucket
    storage_path = f"audio/{filename}"
    
    # Upload the file
    response = supabase.storage.from_(bucket_name).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": content_type}
    )
    
    # Generate and return the public URL so the frontend can optionally play it back
    public_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)
    return public_url
