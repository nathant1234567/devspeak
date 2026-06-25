import os
import json
import google.generativeai as genai

# The SDK automatically looks for the GEMINI_API_KEY environment variable
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def evaluate_interview_audio(audio_file_path: str, question: str = "Tell me about a complex technical problem you solved.") -> dict:
    """
    Uploads the audio to Gemini, prompts it for coaching feedback, and returns the response.
    """
    # Upload the file temporarily to Gemini's servers for processing
    audio_file = genai.upload_file(path=audio_file_path)
    
    model = genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )
    
    prompt = f"""
    You are an expert technical interviewer and coach. The candidate was asked: "{question}"
    
    Listen to their audio response. Provide actionable coaching feedback. 
    You MUST return your response as a JSON object with the following keys:
    "strengths": What they did well.
    "missed_details": What technical details they missed or got wrong.
    "delivery_tips": How they can improve their communication delivery.
    """
    
    response = model.generate_content([prompt, audio_file])
    
    # Clean up the file from Google's servers to ensure privacy
    audio_file.delete()
    
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse coaching feedback."}
