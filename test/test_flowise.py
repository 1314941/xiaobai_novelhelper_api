import requests

API_URL = "http://localhost:3000/api/v1/prediction/b82adddd-3950-4f01-9110-2e4a1283f62f"

def query(payload):
    response = requests.post(API_URL, json=payload)
    return response.json()
    
output = query({
    "question": "Hey, how are you?",
})

print(output)
