import requests

def call_local_api():
    # Call the local FastAPI endpoint
    local_api_url = "http://127.0.0.1:8000/fetch-records"
    local_api_response = requests.get(local_api_url)
    
    # Check if the response is JSON
    try:
        response_json = local_api_response.json()
        print("Local API response:", response_json)
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON response. Raw response text:", local_api_response.text)

# Call the function to execute the API call and print the response
call_local_api()