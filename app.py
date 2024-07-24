from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import logging
from pyairtable import Table
import os
from dotenv import load_dotenv

app = FastAPI()
# Load environment variables from .env file
load_dotenv()

# Access the environment variables
AIRTABLE_API_KEY = os.getenv('AIRTABLE_TOKEN')
BASE_ID = os.getenv('AIRTABLE_APP_ID')
TABLE_NAME = os.getenv('AIRTABLE_TABLE_ID')

# Initialize the Airtable table
table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class TranscribeRequest(BaseModel):
    video_url: str
    api_key: str

def check_record_exists(api_key: str) -> bool:
    try:
        # Use filterByFormula to fetch records that match the API key and are active
        formula = f"AND({{Active}} = TRUE(), {{x-api-key}} = '{api_key}')"

        matching_records = table.all(formula=formula)
        
        logging.debug(f"Number of matching records: {len(matching_records)}")

        # Return True if there is at least one matching record
        return len(matching_records) > 0

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return False

@app.get("/")
async def read_root():
    return {"message": "FastAPI is running"}

@app.post("/transcribe")
async def get_videoid(request: TranscribeRequest):
    api_key = request.api_key.strip()
    logging.debug(f"Received API Key: '{api_key}'")
    
    if not check_record_exists(api_key):
        raise HTTPException(status_code=403, detail="Invalid API Key Airtable")
    
    video_id = request.video_url.split("v=")[1]
    return await root(video_id)

async def root(video_id: str):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    logging.info(f"Transcript for video ID {video_id}: {transcript}")
    formatter = TextFormatter()
    text_formatted = formatter.format_transcript(transcript)
    return {"transcript": text_formatted}
