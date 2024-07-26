from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import logging
from pyairtable import Api
import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
import requests

load_dotenv()

app = FastAPI()
api = Api(os.environ['AIRTABLE_TOKEN'])
serpapi_api_key = os.getenv('SERPER_API_KEY')
youtube_api_key = os.getenv('YOUTUBE_API_KEY')

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class TranscribeRequest(BaseModel):
    video_url: str
    api_key: str

def check_record_exists(api_key: str) -> bool:
    AIRTABLE_APP_ID = os.getenv('AIRTABLE_APP_ID')
    AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')
    print(AIRTABLE_APP_ID)
    print(AIRTABLE_TABLE_ID)
    try:
        # Use filterByFormula to fetch records that match the API key and are active
        table = api.table(AIRTABLE_APP_ID, AIRTABLE_TABLE_ID)
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

async def extract_video_stats(video_id: str):

    params = {
        "engine": "youtube_video",
        "v": video_id,
        "api_key": serpapi_api_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    print(results)
    
    video_data = {
        "title": results.get("title"),
        "created_at": results.get("search_metadata", {}).get("created_at"),
        "description": results.get("description", {}).get("content"),
        "subscribers": results.get("channel", {}).get("subscribers"),
        "channel": results.get("channel", {}).get("name"),
        "views": results.get("views"),
        "likes": results.get("likes"),
        "published_date": results.get("published_date"),
        "thumbnail": results.get("thumbnail"),
        "related_videos": results.get('related_videos', [])
        
    }
    
    # YouTube Data API call to get video duration
    youtube_api_url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=contentDetails&key={youtube_api_key}"
    response = requests.get(youtube_api_url)
    duration_data = response.json()
    # video_data["duration"] = duration_data
    
    if duration_data.get("items"):
        duration = duration_data["items"][0]["contentDetails"]["duration"]
        print(duration)
        video_data["duration"] = duration
    else:
        video_data["duration"] = "Not Available"
    
    return video_data


async def root(video_id: str):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    video_data = await extract_video_stats(video_id)  # Await the async function
    formatter = TextFormatter()
    text_formatted = formatter.format_transcript(transcript)
    return {"transcript": text_formatted, "video_data": video_data}

