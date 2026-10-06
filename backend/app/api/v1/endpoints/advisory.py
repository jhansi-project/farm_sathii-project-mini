import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.advisory import (
    AdvisoryConversationCreate,
    AdvisoryConversationDetail,
    AdvisoryConversationSummary,
    AdvisoryExecutionResponse,
    AdvisoryMessageCreate,
)
from app.schemas.common import StandardResponse
from app.services.advisory import AdvisoryEngine

router = APIRouter(prefix="/advisory", tags=["Advisory"])


@router.post(
    "/conversations",
    response_model=StandardResponse[AdvisoryConversationDetail],
    status_code=status.HTTP_201_CREATED,
    summary="Create Advisory Conversation",
    description="Create a new natural-language agricultural advisory conversation for the authenticated farmer. Optionally ask the first question immediately.",
)
async def create_advisory_conversation(
    payload: AdvisoryConversationCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    engine = AdvisoryEngine(session)
    conv, _ = await engine.create_conversation(
        user_id=current_user.id,
        title=payload.title,
        initial_message=payload.initial_message,
        language=payload.language or "en",
        image_base64=payload.image_base64,
        image_content_type=payload.image_content_type,
        image_filename=payload.image_filename,
        image_path=payload.image_path,
        latitude=payload.latitude,
        longitude=payload.longitude,
        location_name=payload.location_name,
    )
    detail = await engine.get_conversation_detail(conv.id, current_user.id)
    return StandardResponse(
        success=True,
        data=detail,
        message="Advisory conversation created successfully",
    )


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=StandardResponse[AdvisoryExecutionResponse],
    status_code=status.HTTP_200_OK,
    summary="Send Question to Advisory Conversation",
    description="Ask a natural-language agricultural question in an existing conversation. Loads real context, queries the configured advisory provider, enforces safety layer, and persists the dialogue.",
)
async def send_advisory_message(
    conversation_id: uuid.UUID,
    payload: AdvisoryMessageCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    engine = AdvisoryEngine(session)
    execution_result = await engine.ask_question(
        user_id=current_user.id,
        conversation_id=conversation_id,
        question=payload.message_text,
        language=payload.language,
        image_base64=payload.image_base64,
        image_content_type=payload.image_content_type,
        image_filename=payload.image_filename,
        image_path=payload.image_path,
        latitude=payload.latitude,
        longitude=payload.longitude,
        location_name=payload.location_name,
    )
    return StandardResponse(
        success=True,
        data=execution_result,
        message="Advisory response generated successfully",
    )


@router.get(
    "/conversations",
    response_model=StandardResponse[List[AdvisoryConversationSummary]],
    status_code=status.HTTP_200_OK,
    summary="List Advisory Conversations",
    description="Retrieve all past advisory conversations belonging to the authenticated farmer.",
)
async def list_advisory_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    engine = AdvisoryEngine(session)
    conversations = await engine.get_user_conversations(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return StandardResponse(
        success=True,
        data=conversations,
        message="Advisory conversations retrieved successfully",
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=StandardResponse[AdvisoryConversationDetail],
    status_code=status.HTTP_200_OK,
    summary="Get Advisory Conversation Detail",
    description="Retrieve a specific advisory conversation and its complete message history.",
)
async def get_advisory_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    engine = AdvisoryEngine(session)
    detail = await engine.get_conversation_detail(conversation_id, current_user.id)
    return StandardResponse(
        success=True,
        data=detail,
        message="Advisory conversation retrieved successfully",
    )


@router.delete(
    "/conversations/{conversation_id}",
    response_model=StandardResponse[bool],
    status_code=status.HTTP_200_OK,
    summary="Delete Advisory Conversation",
    description="Delete an advisory conversation and its associated messages.",
)
async def delete_advisory_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    engine = AdvisoryEngine(session)
    success = await engine.delete_conversation(conversation_id, current_user.id)
    return StandardResponse(
        success=success,
        data=success,
        message="Advisory conversation deleted successfully",
    )
