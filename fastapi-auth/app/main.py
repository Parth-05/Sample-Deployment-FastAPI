from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db.base import Base
from app.core.config import settings
from app.models import organization as _organization, profile as _profile, trainer as _trainer, client as _client
from app.api.v1.endpoints import auth as auth_router

app = FastAPI(title="Auth API (Supabase)", version="1.0.0")

# would need to update according to frontend urls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         
    allow_credentials=False,     
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    # Dev convenience; disable in prod
    if settings.RUN_DB_CREATE_ALL:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

app.include_router(auth_router.router, prefix="/api/v1/auth")

@app.get("/")
async def root():
    return {"status": "server healthy"}

@app.get("/health")
async def health():
    return {"status": "ok"}
