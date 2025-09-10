from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_db, get_current_user
from app.schemas.profile import ProfileRegister, ProfileOut, Token, Login, AuthData
from app.schemas.response import ApiResponse
from app.crud.profile import crud_profile
from app.core.security import pwd_context
from app.core.security import get_password_hash, verify_password, create_access_token
from app.services.supabase_auth import login_supabase_user, SupabaseAuthError
from app.utils.responses import ok, fail
from app.core.constants import MSG_SUCCESS, MSG_REGISTERED, MSG_USER__EXISTS, MSG_INVALID_CREDENTIALS, MSG_NO_PROFILE


router = APIRouter(tags=["auth"])

# Register new user
@router.post("/register", response_model=ApiResponse[ProfileOut], status_code=status.HTTP_201_CREATED)
async def register(payload: ProfileRegister, db: AsyncSession = Depends(get_db)):
    # Check if email already exists
    existing = await crud_profile.get_by_email(db, email=payload.email)
    if existing:
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=fail(code=status.HTTP_400_BAD_REQUEST, message=MSG_USER__EXISTS).model_dump() #converts the Pydantic model into a plain dict so JSONResponse can serialize it
        )

    # hash the password
    hashed = pwd_context.hash(payload.password)

    # Create profile
    profile = await crud_profile.create_profile_with_role(
        db,
        name=payload.name,
        email=payload.email,
        plain_password=payload.password,     
        hashed_password=hashed,              
        phone=payload.phone,
        user_type=payload.user_type,
        trainer_fields=(payload.trainer.model_dump() if payload.trainer else None),
        client_fields=(payload.client.model_dump() if payload.client else None),
    )

    # return the created profile data
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=ok(profile, message=MSG_REGISTERED, code=status.HTTP_201_CREATED).model_dump()
    )

#  Login User
@router.post("/login")
async def login_json(payload: Login, db: AsyncSession = Depends(get_db)):
    # check credentials with supabase
    try:
        access_token, refresh_token, user_id = await login_supabase_user(
            email=payload.email,
            password=payload.password,
        )
    except SupabaseAuthError:
        # return if invalid credentials
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=fail(code=status.HTTP_400_BAD_REQUEST, message=MSG_INVALID_CREDENTIALS).model_dump()
        )
    # Fetch user profile from DB
    profile = await crud_profile.get_by_id(db, user_id)
    # if profile not found, return error
    if not profile:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=fail(code=status.HTTP_404_NOT_FOUND, message=MSG_NO_PROFILE).model_dump()
        )
    
    # Create token payload
    token_payload = Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
    )

    # ORM -> Pydantic
    profile_out = ProfileOut.model_validate(profile, from_attributes=True)

    data = AuthData(token=token_payload, profile=profile_out).model_dump(mode="json")
    # return the profile data
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ok(data, message=MSG_SUCCESS, code=status.HTTP_200_OK).model_dump(mode="json")
    )

@router.get("/me", response_model=ProfileOut)
async def me(current_user = Depends(get_current_user)):
    return current_user
