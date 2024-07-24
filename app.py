from fastapi import FastAPI, HTTPException
import os
import logging
from pyairtable import Table

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Access the environment variables
AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
AIRTABLE_APP_ID = os.getenv('AIRTABLE_APP_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')

@app.get("/")
async def read_root():
    return {"message": "FastAPI is running"}

@app.get("/fetch-records")
async def fetch_records():
    try:
        if AIRTABLE_TOKEN and AIRTABLE_APP_ID and AIRTABLE_TABLE_ID:
            table = Table(AIRTABLE_TOKEN, AIRTABLE_APP_ID, AIRTABLE_TABLE_ID)
            records = table.all()
            logging.debug(f"Number of records fetched: {len(records)}")
            return {"message": "Records fetched successfully", "records": records}
        else:
            raise HTTPException(status_code=500, detail="Airtable configuration is not available")
    except Exception as e:
        logging.error(f"An error occurred while fetching records: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch records from Airtable")