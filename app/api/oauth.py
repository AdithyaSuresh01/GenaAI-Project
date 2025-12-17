from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from app.db.database import get_session
from app.models.user import User
import os
import httpx

router = APIRouter()

# --- CONFIG ---
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")

# GITHUB CONFIG
GH_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GH_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

# LINKEDIN CONFIG
LI_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LI_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")

# --- 1. GITHUB OAUTH ---

@router.get("/github/login")
def github_login(user_id: int):
    """Redirects user to GitHub for approval"""
    scope = "repo" # Permission to write to repos
    # Pass user_id in 'state' to track who is authenticating
    url = f"https://github.com/login/oauth/authorize?client_id={GH_CLIENT_ID}&scope={scope}&state={str(user_id)}"
    return RedirectResponse(url)

@router.get("/github/callback")
async def github_callback(code: str, state: str, session: Session = Depends(get_session)):
    """Handles the code returned by GitHub"""
    try:
        user_id = int(state)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Exchange Code for Token
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GH_CLIENT_ID,
                "client_secret": GH_SECRET,
                "code": code
            }
        )
        data = resp.json()
    
    access_token = data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to get GitHub token")

    # Save to DB
    user = session.get(User, user_id)
    if user:
        user.github_token = access_token
        session.add(user)
        session.commit()
    
    # Redirect back to Frontend Settings
    # Added user_id param so frontend can verify session
    return RedirectResponse(f"{FRONTEND_URL}/?page=Settings&status=success_gh&user_id={user_id}")


# --- 2. LINKEDIN OAUTH ---

@router.get("/linkedin/login")
def linkedin_login(user_id: int):
    if not LI_CLIENT_ID:
        raise HTTPException(status_code=500, detail="LinkedIn Client ID not configured")

    # Scopes for OpenID Connect + Sharing
    scope = "openid profile email w_member_social"
    
    # Ensure this matches EXACTLY what is in LinkedIn Developer Portal
    redirect_uri = "http://localhost:8000/api/oauth/linkedin/callback"
    
    url = (
        f"https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code"
        f"&client_id={LI_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&state={str(user_id)}"
        f"&scope={scope}"
    )
    return RedirectResponse(url)

@router.get("/linkedin/callback")
async def linkedin_callback(code: str, state: str, session: Session = Depends(get_session)):
    try:
        user_id = int(state)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    redirect_uri = "http://localhost:8000/api/oauth/linkedin/callback"

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": LI_CLIENT_ID,
                "client_secret": LI_SECRET
            }
        )
        data = resp.json()
    
    access_token = data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail=f"Failed to get LinkedIn token: {data}")

    user = session.get(User, user_id)
    if user:
        user.linkedin_token = access_token
        session.add(user)
        session.commit()
    
    return RedirectResponse(f"{FRONTEND_URL}/?page=Settings&status=success_li&user_id={user_id}")
