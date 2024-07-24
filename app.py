from fastapi import FastAPI, HTTPException
import os
import logging
from pyairtable import Table

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Access the environment variables
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')
TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')

@app.get("/")
async def read_root():
    return {"message": "FastAPI is running"}

@app.get("/fetch-records")
async def fetch_records():
    try:
        if AIRTABLE_API_KEY and BASE_ID and TABLE_NAME:
            table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
            records = table.all()
            logging.debug(f"Number of records fetched: {len(records)}")
            return {"message": "Records fetched successfully", "records": records}
        else:
            raise HTTPException(status_code=500, detail="Airtable configuration is not available")
    except Exception as e:
        logging.error(f"An error occurred while fetching records: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch records from Airtable")