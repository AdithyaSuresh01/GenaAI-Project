import requests

# Base URL for the FastAPI Backend
# If running via Docker, this might need to be the container name
API_BASE_URL = "http://127.0.0.1:8000/api/v1" 

# Separate base for OAuth, as it might not be under /api/v1 depending on main.py
API_ROOT_URL = "http://127.0.0.1:8000"

def login_api(email, password):
    """
    Authenticates user and returns user data (id, name, email, profile_data).
    """
    try:
        resp = requests.post(f"{API_BASE_URL}/login", json={"email": email, "password": password}, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to backend.")
        return None
    except Exception as e:
        print(f"Login Error: {e}")
        return None

def signup_api(email, password, fullname):
    """
    Registers a new user.
    """
    try:
        resp = requests.post(f"{API_BASE_URL}/signup", json={"email": email, "password": password, "full_name": fullname}, timeout=5)
        return resp.status_code == 200
    except requests.exceptions.ConnectionError:
        return False
    except: 
        return False
