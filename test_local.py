import requests

def call_local_api():
    # Call the local FastAPI endpoint
    local_api_url = "http://127.0.0.1:8000/transcribe"
    local_api_response = requests.post(
        local_api_url,
        json={"video_url": "https://www.youtube.com/watch?v=q9eOF4lw5sA", "api_key": "qE7uKfYLoBxJfm"}
    )
    
    # Check if the response is JSON
    try:
        response_json = local_api_response.json()
        print("Local API response:", response_json)
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON response. Raw response text:", local_api_response.text)

# Call the function to execute the API call and print the response
call_local_api()