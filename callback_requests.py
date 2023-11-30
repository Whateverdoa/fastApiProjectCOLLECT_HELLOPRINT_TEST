import json
import os

import jwt
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

callback_url = os.getenv("CALLBACK_URL")  # Replace with your actual callback URL
client_id = os.getenv("CLIENT_ID")  # Replace with your actual client ID
client_secret = os.getenv("CLIENT_SECRET")  # Replace with your actual client secret
jwt_token = os.getenv("JWT_TOKEN")  # Replace with your actual JWT token

payload = {
    "sub": client_id,  # Subject (client ID)
    "aud": callback_url,  # Audience (callback URL)
    "exp": datetime.utcnow() + timedelta(hours=1)  # Expiration time (e.g., 1 hour from now)
}

# jwt_token = jwt.encode(payload, client_secret, algorithm="HS256")


headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

callback_data = {
    "status": "200 OK"

    # Add more data as needed
}

try:
    response = requests.post(callback_url, json=callback_data, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        print("Callback successful")
    else:
        print(f"Callback failed with status code {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error sending callback: {str(e)}")


def send_callback_request(order_reference,supplier_name, authorization_token, status="in_production"):
    # Define the URL
    url = f"https://supplier-integration-api.helloprint.com/orders/callback/{supplier_name}"

    # Define the headers including the authorization token
    headers = {
        "authorization-token": authorization_token,
        "content-type": "application/json"
    }

    # Define the payload data as a dictionary
    payload = {
        "orderReference": order_reference,  #"949939__1308041",
        "status": status
    }

    # Send the POST request
    response = requests.post(url, headers=headers, json=payload)

    # Check the response
    if response.status_code == 200:
        return "Request successful"
    else:
        return f"Request failed with status code {response.status_code}: {response.text}"


# Example usage:
supplier_name = "vilaetiketten"
authorization_token = jwt_token

# By default, status is "in_production"
result = send_callback_request(supplier_name, authorization_token)
print(result)

# You can also specify a different status if needed
# result = send_callback_request(supplier_name, authorization_token, status="shipped")
# print(result)
