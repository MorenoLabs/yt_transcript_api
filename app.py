from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import logging

app = FastAPI()

class TranscribeRequest(BaseModel):
    video_url: str
    api_key: str

def verify_api_key(request: TranscribeRequest):
    if request.api_key != "test":  # Replace with your actual API key
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.get("/")
async def read_root():
    return {"message": "FastAPI is running"}

@app.post("/transcribe")
async def get_videoid(request: TranscribeRequest, verified: None = Depends(verify_api_key)):
    video_id = request.video_url.split("v=")[1]
    return await root(video_id)

async def root(video_id: str):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    logging.info(f"Transcript for video ID {video_id}: {transcript}")
    formatter = TextFormatter()
    text_formatted = formatter.format_transcript(transcript)
    return {"transcript": text_formatted}