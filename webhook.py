import requests
import json

def send_webhook():
    # Define the webhook URL
    webhook_url = "https://https://hook.eu2.make.com/wx5sw8683r5jieos9hnaef39ox7jsseh"
    
    # Define the JSON payload
    payload = {
        "video_url": "https://www.youtube.com/watch?v=fJwcfIYCbo8",
        "api_key": "qE7uKfYLoBxJfm"
    }
    
    # Define headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Print the payload to verify its structure
    print("Payload being sent:", json.dumps(payload, indent=4))
    
    # Send the POST request
    response = requests.post(webhook_url, json=payload, headers=headers)
    
    # Print the response
    try:
        response_json = response.json()
        print("Webhook response:", response_json)
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON response. Raw response text:", response.text)

# Call the function to send the webhook
send_webhook()