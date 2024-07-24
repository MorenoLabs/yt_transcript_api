from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import logging
from pyairtable import Table
import os
# from dotenv import load_dotenv

app = FastAPI()

# Load environment variables from .env file
# load_dotenv()

# Access the environment variables
AIRTABLE_API_KEY = os.getenv('AIRTABLE_TOKEN')
logging.debug(f"TOKEN: {AIRTABLE_API_KEY }")
BASE_ID = os.getenv('AIRTABLE_APP_ID')
logging.debug(f"Airtable Base ID: {BASE_ID}")
TABLE_NAME = os.getenv('AIRTABLE_TABLE_ID')
logging.debug(f"Airtable Table Name: {TABLE_NAME}")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.get("/")
async def read_root():
    return {"message": "FastAPI is running"}

@app.get("/check-token")
async def check_token():
    AIRTABLE_API_KEY = 'pateFFJHWZvAtX53C.fa3792abeedf15e33e69c0f1e965bb25f79f24b39566ac155fc320cc1ffac165'
    try:
        if AIRTABLE_API_KEY:
            table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
            records = table.all()
            logging.debug(f"Number of records fetched: {len(records)}")
            if records:
                # Return the first few records for inspection
                sample_records = records[:5]  # Return first 5 records for brevity
                return {"message": "Records fetched successfully", "records": sample_records}
            else:
                return {"message": "No records found"}
        else:
            raise HTTPException(status_code=500, detail="Airtable token is not available")
    except Exception as e:
        logging.error(f"An error occurred while fetching records: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch records from Airtable")
