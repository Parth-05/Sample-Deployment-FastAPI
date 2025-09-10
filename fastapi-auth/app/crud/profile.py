from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.profile import Profile
from app.models.trainer import Trainer
from app.models.client import Client
from app.models.enums import UserRole
from app.services.supabase_auth import signup_and_get_tokens
from app.schemas.profile import Token, AuthData

class CRUDProfile:
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[Profile]:
        res = await db.execute(select(Profile).where(Profile.email == email))
        return res.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, id: str) -> Optional[Profile]:
        return await db.get(Profile, id)

    async def create_profile_with_role(
        self,
        db: AsyncSession,
        *,  # everything after must be passed as keyword args
        name: Optional[str],
        email: str,
        plain_password: str,             
        hashed_password: Optional[str],  
        phone: Optional[str],
        user_type: Optional[UserRole],
        trainer_fields: Optional[dict] = None,
        client_fields: Optional[dict] = None,
    ) -> Profile:
        # 1) Create in Supabase Auth -> returns the auth user id (satisfies FK)
        sess = await signup_and_get_tokens(
            email=email,
            password=plain_password,
            full_name=name,
            phone=phone,
            role=(user_type.value if user_type else None),
        )

        # 2) Insert into profiles using the SAME id
        profile = Profile(
            id=sess.user_id,
            name=name,
            email=email,
            password=hashed_password,   
            phone=phone,
            user_type=user_type,
            is_active=False,
        )
        db.add(profile)
        await db.flush()

        if user_type == UserRole.trainer:
            # normalize certifications to a list[str] (TEXT[] in DB)
            certs_in = (trainer_fields or {}).get("certifications")
            if isinstance(certs_in, str):
                certs: Optional[List[str]] = [c.strip() for c in certs_in.split(",") if c.strip()]
            else:
                certs = certs_in
            years = (trainer_fields or {}).get("years_exp")
            if years is None:
                years = 0  # default to 0
            else:
                years = int(years)  

            trainer = Trainer(
                id=profile.id,
                bio=(trainer_fields or {}).get("bio"),
                certifications=certs,
                years_exp=years,
                organization_id=(trainer_fields or {}).get("organization_id"),
            )
            db.add(trainer)
        elif user_type == UserRole.client:
            client = Client(
                id=profile.id,
                fitness_goal=(client_fields or {}).get("fitness_goal"),
            )
            db.add(client)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise

        await db.refresh(profile)

        token_payload = Token(access_token=sess.access_token, token_type="bearer", refresh_token=sess.refresh_token)
        data = AuthData(token=token_payload, profile=profile)
        return data

crud_profile = CRUDProfile()
