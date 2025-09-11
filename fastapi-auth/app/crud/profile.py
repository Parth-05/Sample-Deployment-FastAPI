# from typing import Optional, List
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from sqlalchemy.exc import IntegrityError
# from app.models.profile import Profile
# from app.models.trainer import Trainer
# from app.models.client import Client
# from app.models.enums import UserRole
# from app.services.supabase_auth import signup_and_get_tokens
# from app.schemas.profile import Token, AuthData
# import logging, traceback

# class CRUDProfile:
#     async def get_by_email(self, db: AsyncSession, email: str) -> Optional[Profile]:
#         try:
#             res = await db.execute(select(Profile).where(Profile.email == email))
#             return res.scalar_one_or_none()
#         except Exception as e:
#             print(f"DB error get_by_email email={email}: {e}\n{traceback.format_exc()}", flush=True)
#             logging.error("DB error get_by_email email=%s", email)
#             raise e

#     async def get_by_id(self, db: AsyncSession, id: str) -> Optional[Profile]:
#         try:
#             return await db.get(Profile, id)
#         except Exception as e:
#             print(f"DB error get_by_id id={id}: {e}\n{traceback.format_exc()}", flush=True)
#             logging.error("DB error get_by_id id=%s", id)
#             raise e

#     async def create_profile_with_role(
#         self,
#         db: AsyncSession,
#         *,  # everything after must be passed as keyword args
#         name: Optional[str],
#         email: str,
#         plain_password: str,             
#         hashed_password: Optional[str],  
#         phone: Optional[str],
#         user_type: Optional[UserRole],
#         trainer_fields: Optional[dict] = None,
#         client_fields: Optional[dict] = None,
#     ) -> AuthData:
#         try:
#             # 1) Create in Supabase Auth -> returns the auth user id (satisfies FK)
#             sess = await signup_and_get_tokens(
#                 email=email,
#                 password=plain_password,
#                 full_name=name,
#                 phone=phone,
#                 role=(user_type.value if user_type else None),
#             )
#         except Exception as e:
#             print(f"Supabase signup failed for email: {e}\n{traceback.format_exc()}", flush=True)
#             logging.error(f"Supabase signup failed for email={email}: {e}")
#             raise e

#         # 2) Insert into profiles using the SAME id
#         profile = Profile(
#             id=sess.user_id,
#             name=name,
#             email=email,
#             password=hashed_password,   
#             phone=phone,
#             user_type=user_type,
#             is_active=False,
#         )
#         db.add(profile)
#         await db.flush()

#         if user_type == UserRole.trainer:
#             # normalize certifications to a list[str] (TEXT[] in DB)
#             certs_in = (trainer_fields or {}).get("certifications")
#             if isinstance(certs_in, str):
#                 certs: Optional[List[str]] = [c.strip() for c in certs_in.split(",") if c.strip()]
#             else:
#                 certs = certs_in
#             years = (trainer_fields or {}).get("years_exp")
#             if years is None:
#                 years = 0  # default to 0
#             else:
#                 years = int(years)  

#             trainer = Trainer(
#                 id=profile.id,
#                 bio=(trainer_fields or {}).get("bio"),
#                 certifications=certs,
#                 years_exp=years,
#                 organization_id=(trainer_fields or {}).get("organization_id"),
#             )
#             db.add(trainer)
#         elif user_type == UserRole.client:
#             client = Client(
#                 id=profile.id,
#                 fitness_goal=(client_fields or {}).get("fitness_goal"),
#             )
#             db.add(client)

#         try:
#             await db.commit()
#         except Exception as e:
#             await db.rollback()
#             raise

#         await db.refresh(profile)

#         token_payload = Token(access_token=sess.access_token, token_type="bearer", refresh_token=sess.refresh_token)
#         data = AuthData(token=token_payload, profile=profile)
#         return data

# crud_profile = CRUDProfile()


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
import traceback

class CRUDProfile:
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[Profile]:
        try:
            res = await db.execute(select(Profile).where(Profile.email == email))
            return res.scalar_one_or_none()
        except Exception as e:
            print(f"DB error get_by_email email={email}: {e}\n{traceback.format_exc()}", flush=True)
            raise

    async def get_by_id(self, db: AsyncSession, id: str) -> Optional[Profile]:
        try:
            return await db.get(Profile, id)
        except Exception as e:
            print(f"DB error get_by_id id={id}: {e}\n{traceback.format_exc()}", flush=True)
            raise

    async def create_profile_with_role(
        self,
        db: AsyncSession,
        *,
        name: Optional[str],
        email: str,
        plain_password: str,             # DO NOT print this
        hashed_password: Optional[str],
        phone: Optional[str],
        user_type: Optional[UserRole],
        trainer_fields: Optional[dict] = None,
        client_fields: Optional[dict] = None,
    ) -> AuthData:
        # 1) Create in Supabase Auth
        try:
            sess = await signup_and_get_tokens(
                email=email,
                password=plain_password,
                full_name=name,
                phone=phone,
                role=(user_type.value if user_type else None),
            )
            print(f"Supabase signup OK email={email} user_id={sess.user_id}", flush=True)
        except Exception as e:
            print(f"Supabase signup FAILED email={email}: {e}\n{traceback.format_exc()}", flush=True)
            raise

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
        try:
            db.add(profile)
            await db.flush()
            print(f"DB flush OK profile_id={profile.id}", flush=True)
        except Exception as e:
            print(f"DB flush FAILED email={email}: {e}\n{traceback.format_exc()}", flush=True)
            raise

        # 3) Optional role rows
        try:
            if user_type == UserRole.trainer:
                certs_in = (trainer_fields or {}).get("certifications")
                if isinstance(certs_in, str):
                    certs: Optional[List[str]] = [c.strip() for c in certs_in.split(",") if c.strip()]
                else:
                    certs = certs_in

                years_raw = (trainer_fields or {}).get("years_exp")
                try:
                    years = int(years_raw) if years_raw is not None else 0
                except (TypeError, ValueError):
                    print(f"Invalid years_exp={years_raw} for email={email}; defaulting to 0", flush=True)
                    years = 0

                trainer = Trainer(
                    id=profile.id,
                    bio=(trainer_fields or {}).get("bio"),
                    certifications=certs,
                    years_exp=years,
                    organization_id=(trainer_fields or {}).get("organization_id"),
                )
                db.add(trainer)
                print(f"Prepared Trainer row for profile_id={profile.id}", flush=True)

            elif user_type == UserRole.client:
                client = Client(
                    id=profile.id,
                    fitness_goal=(client_fields or {}).get("fitness_goal"),
                )
                db.add(client)
                print(f"Prepared Client row for profile_id={profile.id}", flush=True)

        except Exception as e:
            print(f"Role row build/add FAILED profile_id={profile.id}: {e}\n{traceback.format_exc()}", flush=True)
            raise

        # 4) Commit
        try:
            await db.commit()
            print(f"DB commit OK profile_id={profile.id}", flush=True)
        except IntegrityError as e:
            await db.rollback()
            print(f"DB commit IntegrityError profile_id={profile.id}: {e}\n{traceback.format_exc()}", flush=True)
            raise
        except Exception as e:
            await db.rollback()
            print(f"DB commit FAILED profile_id={profile.id}: {e}\n{traceback.format_exc()}", flush=True)
            raise

        # 5) Refresh
        try:
            await db.refresh(profile)
            print(f"DB refresh OK profile_id={profile.id}", flush=True)
        except Exception as e:
            print(f"DB refresh FAILED profile_id={profile.id}: {e}\n{traceback.format_exc()}", flush=True)
            raise

        token_payload = Token(
            access_token=sess.access_token,
            token_type="bearer",
            refresh_token=sess.refresh_token
        )
        data = AuthData(token=token_payload, profile=profile)
        print(f"Register OK user_id={sess.user_id} role={user_type}", flush=True)
        return data

crud_profile = CRUDProfile()
