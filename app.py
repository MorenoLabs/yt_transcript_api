import logging
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from youtube_transcript_api._errors import TranscriptsDisabled
from urllib.parse import urlparse, parse_qs
import requests

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

class TranscribeRequest(BaseModel):
    video_url: str
    api_key: str

class CustomYouTubeTranscriptApi(YouTubeTranscriptApi):
    @classmethod
    def get_transcript(cls, video_id, *args, **kwargs):
        custom_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        return super().get_transcript(video_id, *args, **kwargs, proxies=None, cookies=None, headers=custom_headers)

def verify_api_key(request: TranscribeRequest):
    if request.api_key != "test":  # Replace with your actual API key
        raise HTTPException(status_code=403, detail="Invalid API Key")

def extract_video_id(url):
    logger.debug(f"Extracting video ID from URL: {url}")
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    logger.error(f"Failed to extract video ID from URL: {url}")
    return None

@app.get("/")
async def read_root():
    return {"message": "FastAPI is running"}

@app.post("/transcribe")
async def get_videoid(request: TranscribeRequest, verified: None = Depends(verify_api_key)):
    logger.debug(f"Received transcription request for URL: {request.video_url}")
    video_id = extract_video_id(request.video_url)
    if not video_id:
        logger.error(f"Failed to extract video ID from URL: {request.video_url}")
        raise HTTPException(status_code=400, detail="Could not extract video ID from URL")
    logger.debug(f"Extracted video ID: {video_id}")
    return await root(video_id)

async def root(video_id: str):
    logger.debug(f"Attempting to get transcript for video ID: {video_id}")
    try:
        logger.debug("Calling CustomYouTubeTranscriptApi.get_transcript")
        transcript = CustomYouTubeTranscriptApi.get_transcript(video_id)
        logger.debug(f"Transcript retrieved successfully. Length: {len(transcript)}")
        formatter = TextFormatter()
        text_formatted = formatter.format_transcript(transcript)
        logger.debug("Transcript formatted successfully")
        return {"transcript": text_formatted}
    except TranscriptsDisabled:
        logger.error(f"Transcripts are disabled for video {video_id}")
        raise HTTPException(status_code=404, detail="Transcripts are not available for this video")
    except Exception as e:
        logger.error(f"Error occurred while processing video {video_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)