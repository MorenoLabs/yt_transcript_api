from fastapi import FastAPI
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

app = FastAPI()

@app.get("/transcribe")
async def get_videoid(video_url: str):
    video_id = video_url.split('v=')[1]
    return await root(video_id)

async def root(video_id: str):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    formatter = TextFormatter()
    text_formatted = formatter.format_transcript(transcript)
    return {"transcript": text_formatted}