from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.schemas.common import StandardResponse
from app.schemas.user import UserWithProfileResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=StandardResponse[TokenResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new farmer account",
)
async def register(
    user_in: UserRegisterRequest,
    session: AsyncSession = Depends(get_db),
) -> StandardResponse[TokenResponse]:
    auth_service = AuthService(session)
    tokens = await auth_service.register(user_in)
    return StandardResponse(
        success=True,
        data=tokens,
        message="Farmer account registered successfully.",
    )


@router.post(
    "/login",
    response_model=StandardResponse[TokenResponse],
    summary="Authenticate farmer credentials",
)
async def login(
    login_in: UserLoginRequest,
    session: AsyncSession = Depends(get_db),
) -> StandardResponse[TokenResponse]:
    auth_service = AuthService(session)
    tokens = await auth_service.login(login_in)
    return StandardResponse(
        success=True,
        data=tokens,
        message="Login successful.",
    )


@router.post(
    "/refresh",
    response_model=StandardResponse[AccessTokenResponse],
    summary="Refresh an expired access token",
)
async def refresh_token(
    refresh_in: TokenRefreshRequest,
    session: AsyncSession = Depends(get_db),
) -> StandardResponse[AccessTokenResponse]:
    auth_service = AuthService(session)
    new_token = await auth_service.refresh_access_token(refresh_in)
    return StandardResponse(
        success=True,
        data=new_token,
        message="Access token refreshed successfully.",
    )


@router.get(
    "/me",
    response_model=StandardResponse[UserWithProfileResponse],
    summary="Fetch current farmer identity and profile",
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> StandardResponse[UserWithProfileResponse]:
    user_data = UserWithProfileResponse.model_validate(current_user)
    return StandardResponse(
        success=True,
        data=user_data,
        message="Current user identity retrieved successfully.",
    )
