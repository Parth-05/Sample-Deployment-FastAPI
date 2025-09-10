import httpx
from app.core.config import settings
from pydantic import BaseModel

class SupabaseSession(BaseModel):
    access_token: str | None
    refresh_token: str | None
    user_id: str

class SupabaseAuthError(RuntimeError):
    pass

async def signup_and_get_tokens(
    *, email: str, password: str, full_name: str | None = None, phone: str | None = None, role: str | None = None
) -> SupabaseSession:
    """
    Create a user (confirmed) via Admin API, then sign in to get tokens.
    Use this in your /register to return tokens immediately.
    """
    # Create user via Admin API
    user_id = await create_supabase_user(
        email=email, password=password, full_name=full_name, phone=phone, role=role
    )
    # Login to get tokens
    access_token, refresh_token, _ = await login_supabase_user(email=email, password=password)
    return SupabaseSession(access_token=access_token, refresh_token=refresh_token, user_id=user_id)

# create user via Supabase Admin API
async def create_supabase_user(
    *,
    email: str,
    password: str,
    full_name: str | None = None,
    phone: str | None = None,
    role: str | None = None,
) -> str:
    """
    Create a user via Supabase Admin API and return the Auth user id (UUID).
    Requires SUPABASE_SERVICE_ROLE_KEY.
    """
    url = f"{settings.SUPABASE_URL}/auth/v1/admin/users"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "password": password,      
        "email_confirm": True,     
        "user_metadata": {
            "full_name": full_name,
            "phone": phone,
            "role": role,
        },
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(url, headers=headers, json=payload)
    # 200/201 typical; surface useful errors otherwise
    if resp.status_code not in (200, 201):
        raise SupabaseAuthError(f"Create user failed: {resp.status_code} {resp.text}")
    data = resp.json()
    user = data.get("user") or data
    user_id = user.get("id")
    if not user_id:
        raise SupabaseAuthError(f"No user id in response: {data}")
    return user_id


async def login_supabase_user(email: str, password: str):
    """
    Password grant against Supabase GoTrue.
    Returns (access_token, refresh_token, user_id dict).
    """
    url = f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": settings.SUPABASE_ANON_KEY,           # anon/public key
        "Content-Type": "application/json",
    }
    payload = {"email": email, "password": password}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, headers=headers, json=payload)

    if resp.status_code != 200:
        raise SupabaseAuthError(f"Login failed: {resp.status_code} {resp.text}")

    data = resp.json()
    # data contains access_token, refresh_token, token_type, user, etc.
    return data["access_token"], data.get("refresh_token"), data.get("user", {}).get("id")