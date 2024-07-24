import requests

def call_external_api():
    # Call the external API
    external_api_url = "https://oyster-app-2-4s4pa.ondigitalocean.app/transcribe"
    external_api_response = requests.post(
        external_api_url,
        json={"video_url": "https://www.youtube.com/watch?v=JLEDwO7JEK4", "api_key": "test"}
    )
    
    # Check if the response is JSON
    try:
        response_json = external_api_response.json()
        print("External API response:", response_json)
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON response. Raw response text:", external_api_response.text)

# Call the function to execute the API call and print the response
call_external_api()