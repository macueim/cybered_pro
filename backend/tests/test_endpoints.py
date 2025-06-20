import requests

# Base URL of your API
base_url = "http://127.0.0.1:8000"

# Test health check
response = requests.get(f"{base_url}/")
print(f"Health check: {response.json()}")

# Test authentication (login)
login_data = {"username": "test@example.com", "password": "securepassword"}
response = requests.post(f"{base_url}/api/v1/users/login", json=login_data)
token = response.json().get("access_token")

# Use the token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{base_url}/api/v1/users/me", headers=headers)
print(f"Current user: {response.json()}")