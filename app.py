from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import logging
from pyairtable import Api
import os
from dotenv import load_dotenv

app = FastAPI()
# Load environment variables from .env file
load_dotenv()

# Access the environment variables
AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
AIRTABLE_APP_ID = os.getenv('AIRTABLE_APP_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')

api = Api(AIRTABLE_TOKEN)
table = api.table(AIRTABLE_APP_ID, AIRTABLE_TABLE_ID)

class TranscribeRequest(BaseModel):
    video_url: str
    api_key: str

def check_record_exists(request: TranscribeRequest):
    try:
        # Fetch all records from the table
        api_key = request.api_key.strip()
        logging.alert(f"API Key: {api_key}")
        all_records = table.all()
        
        # Check if at least one record meets the criteria
        for record in all_records:
            if record['fields'].get('Active') and record['fields'].get('api_test') == api_key:
                print(f"Record found: {record}")
                print(f"API Key: {record['fields'].get('x-api-key')}")
                print(f"Active: {record['fields'].get('Active')}")
                print(f"Request API Key: {request.api_key}")
                return True
        return False

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

@app.get("/")
async def read_root():
    return {"message": "FastAPI is running"}

@app.post("/transcribe")
async def get_videoid(request: TranscribeRequest):
    if not check_record_exists(request):
        raise HTTPException(status_code=403, detail=f"Invalid API Key: {request.api_key}")
    
    video_id = request.video_url.split("v=")[1]
    return await root(video_id)

async def root(video_id: str):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    logging.info(f"Transcript for video ID {video_id}: {transcript}")
    formatter = TextFormatter()
    text_formatted = formatter.format_transcript(transcript)
    return {"transcript": text_formatted}