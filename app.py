from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import logging
from pyairtable import Table
import os
# from dotenv import load_dotenv

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class TranscribeRequest(BaseModel):
    video_url: str
    api_key: str

def check_record_exists(api_key: str) -> bool:
    AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
    AIRTABLE_APP_ID = os.getenv('AIRTABLE_APP_ID')
    AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')
    try:
        # Use filterByFormula to fetch records that match the API key and are active
        table = Table(AIRTABLE_TOKEN, AIRTABLE_APP_ID, AIRTABLE_TABLE_ID)
        formula = f"AND({{Active}} = TRUE(), {{x-api-key}} = '{api_key}')"

        matching_records = table.all(formula=formula)
        # print(f"Number of matching records: {len(matching_records)}")
        
        logging.debug(f"Number of matching records: {len(matching_records)}")

        # Return True if there is at least one matching record
        return True

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return False

@app.get("/")
async def read_root():
    return {"message": "FastAPI is running"}

@app.post("/transcribe")

async def get_videoid(request: TranscribeRequest):
    api_key = request.api_key.strip()

    if not check_record_exists(api_key):
        raise HTTPException(status_code=403, detail="Invalid API Key Airtable")
    
    video_id = request.video_url.split("v=")[1]
    return await root(video_id)

async def root(video_id: str):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    # logging.info(f"Transcript for video ID {video_id}: {transcript}")
    formatter = TextFormatter()
    text_formatted = formatter.format_transcript(transcript)
    return {"transcript": text_formatted}


@app.get("/fetch-records")
async def fetch_records():
    # Access the environment variables within the function
    AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
    AIRTABLE_APP_ID = os.getenv('AIRTABLE_APP_ID')
    AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')
    print(AIRTABLE_TOKEN)
    print(AIRTABLE_APP_ID)
    print(AIRTABLE_TABLE_ID)
    try:
        if AIRTABLE_TOKEN and AIRTABLE_APP_ID and AIRTABLE_TABLE_ID:
            logging.debug(AIRTABLE_TOKEN)
            table = Table(AIRTABLE_TOKEN, AIRTABLE_APP_ID, AIRTABLE_TABLE_ID)
            records = table.all()
            logging.debug(f"Number of records fetched: {len(records)}")
            return {
                "message": "Records fetched successfully",
                "records": records,
                "api_key": AIRTABLE_TOKEN,
                "base_id": AIRTABLE_APP_ID,
                "table_name": AIRTABLE_TABLE_ID
            }
        else:
            raise HTTPException(status_code=500, detail="Airtable configuration is not available")
    except Exception as e:
        logging.error(f"An error occurred while fetching records: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch records from Airtable")
