import uuid
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import (
    AccessTokenResponse,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.schemas.user import UserWithProfileResponse
from app.services.profile_service import ProfileService


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.profile_service = ProfileService(session)

    async def register(self, user_in: UserRegisterRequest) -> TokenResponse:
        # Check uniqueness of phone
        if user_in.phone:
            existing_phone = await self.user_repo.get_by_phone(user_in.phone)
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this phone number already exists.",
                )

        # Check uniqueness of email
        if user_in.email:
            existing_email = await self.user_repo.get_by_email(str(user_in.email))
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email address already exists.",
                )

        # Create user
        hashed_password = get_password_hash(user_in.password)
        new_user = await self.user_repo.create(
            full_name=user_in.full_name,
            phone=user_in.phone,
            email=str(user_in.email) if user_in.email else None,
            password_hash=hashed_password,
            is_active=True,
        )

        # Create default profile
        profile = await self.profile_service.create_default_profile(
            user_id=new_user.id,
            preferred_language=user_in.preferred_language,
        )
        new_user.profile = profile

        # Generate tokens
        access_token = create_access_token(new_user.id)
        refresh_token = create_refresh_token(new_user.id)

        user_with_profile = UserWithProfileResponse.model_validate(new_user)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_with_profile,
        )

    async def login(self, login_in: UserLoginRequest) -> TokenResponse:
        identifier = login_in.identifier.strip()
        user: Optional[User] = None

        if "@" in identifier:
            user = await self.user_repo.get_by_email(identifier)
        else:
            user = await self.user_repo.get_by_phone(identifier)
            if not user:
                # Fallback to checking email just in case
                user = await self.user_repo.get_by_email(identifier)

        if not user or not verify_password(login_in.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect phone/email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive. Please contact support.",
            )

        # Fetch profile
        user_with_rel = await self.user_repo.get_with_profile(user.id)
        if not user_with_rel:
            user_with_rel = user

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        user_with_profile = UserWithProfileResponse.model_validate(user_with_rel)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_with_profile,
        )

    async def refresh_access_token(
        self, refresh_in: TokenRefreshRequest
    ) -> AccessTokenResponse:
        try:
            payload = decode_token(refresh_in.refresh_token)
            token_type = payload.get("type")
            user_id = payload.get("sub")
            if token_type != "refresh" or not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token payload.",
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
            )

        user = await self.user_repo.get(uuid.UUID(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User inactive or no longer exists.",
            )

        new_access_token = create_access_token(user.id)
        return AccessTokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
