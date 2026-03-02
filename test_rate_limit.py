import requests
import json
import time

url = 'http://127.0.0.1:8000/api/v1/core/register/'
headers = {'Content-Type': 'application/json'}
data = {
    "first_name": "Test",
    "last_name": "User",
    "email": "test@test.edu",
    "password": "password123"
}

print("Testing Registration Rate Limit (otp_request) - Limit 3/hour")
for i in range(1, 6):
    
    # We alter the email slightly each time to bypass the "email already exists" unique constraint before hitting the throttle
    data["email"] = f"testX{i}@test.edu"
    
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=5)
        print(f"Request {i} ({time.time() - start_time:.2f}s) - Status Code: {response.status_code}")
        if response.status_code == 429:
            print("Rate Limit Hit Successfully!")
            print(response.json())
            break
        elif response.status_code not in [200, 201]:
            print(response.json())
    except requests.exceptions.Timeout:
        print(f"Request {i} timed out after 5 seconds. The dev server is likely hanging on the Email dispatch.")
        break

