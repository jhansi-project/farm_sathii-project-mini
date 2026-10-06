import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.languages import DEFAULT_LANGUAGE, is_language_supported
from app.models.advisory import AdvisoryConversation
from app.repositories.advisory_repo import AdvisoryRepository
from app.schemas.advisory import (
    AdvisoryConversationDetail,
    AdvisoryConversationSummary,
    AdvisoryExecutionResponse,
    AdvisoryMessageResponse,
    AdvisoryProviderStatus,
)
from app.services.advisory.context_assembler import ContextAssembler
from app.services.advisory.image_handler import image_handler
from app.services.advisory.providers.base import (
    AdvisoryPromptRequest,
    AdvisoryProviderResult,
)
from app.services.advisory.providers.router import (
    ProviderRouter,
    default_provider_router,
)
from app.services.advisory.safety_layer import SafetyLayer


class AdvisoryEngine:
    """
    Core orchestrator for FarmSathi natural-language agricultural advisory.
    Integrates Context Assembler, Provider Router, Safety Layer, Multimodal Image Handler,
    Multilingual dispatch, and DB persistence.
    Contains NO provider-specific implementation details.
    """

    def __init__(
        self,
        session: AsyncSession,
        router: Optional[ProviderRouter] = None,
    ):
        self.session = session
        self.router = router or default_provider_router
        self.advisory_repo = AdvisoryRepository(session)
        self.context_assembler = ContextAssembler(session)
        self.safety_layer = SafetyLayer()

    async def create_conversation(
        self,
        user_id: uuid.UUID,
        title: Optional[str] = None,
        initial_message: Optional[str] = None,
        language: str = DEFAULT_LANGUAGE,
        image_base64: Optional[str] = None,
        image_content_type: Optional[str] = None,
        image_filename: Optional[str] = None,
        image_path: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        location_name: Optional[str] = None,
    ) -> Tuple[AdvisoryConversation, Optional[AdvisoryExecutionResponse]]:
        """
        Creates an advisory conversation for an authenticated user, optionally
        processing the first farmer question (with optional image) immediately.
        """
        clean_lang = language.strip().lower() if language else DEFAULT_LANGUAGE
        if not is_language_supported(clean_lang):
            clean_lang = DEFAULT_LANGUAGE

        if not title:
            if initial_message and initial_message.strip():
                clean_q = initial_message.strip()
                title = clean_q[:42] + "..." if len(clean_q) > 45 else clean_q
            else:
                title = "Agricultural Advisory Session"

        conv = await self.advisory_repo.create_conversation(
            user_id=user_id,
            title=title,
            language=clean_lang,
        )

        exec_res: Optional[AdvisoryExecutionResponse] = None
        if initial_message and initial_message.strip():
            exec_res = await self.ask_question(
                user_id=user_id,
                conversation_id=conv.id,
                question=initial_message.strip(),
                language=clean_lang,
                image_base64=image_base64,
                image_content_type=image_content_type,
                image_filename=image_filename,
                image_path=image_path,
                latitude=latitude,
                longitude=longitude,
                location_name=location_name,
            )

        return conv, exec_res

    async def ask_question(
        self,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        question: str,
        language: Optional[str] = None,
        image_base64: Optional[str] = None,
        image_content_type: Optional[str] = None,
        image_filename: Optional[str] = None,
        image_path: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        location_name: Optional[str] = None,
    ) -> AdvisoryExecutionResponse:
        """
        Processes a farmer's question in an existing conversation:
        1. Validates request and language
        2. Verifies ownership
        3. Decodes & validates image (if supplied)
        4. Persists farmer question and image metadata
        5. Gathers authentic context (profile, crop rec, disease, weather, history, image)
        6. Enforces Provider Capability check (text/multimodal/multilingual)
        7. Calls ProviderRouter
        8. Applies Safety Layer & agricultural disclaimers
        9. Persists assistant message
        10. Returns structured response
        """
        clean_q = question.strip() if question else ""
        if not clean_q:
            raise HTTPException(
                status_code=422,
                detail="Farmer question cannot be empty.",
            )

        # Verify conversation exists and belongs to the user
        conv = await self.advisory_repo.get_by_id_and_user_id(conversation_id, user_id)
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Advisory conversation not found or access denied.",
            )

        # Determine effective language
        effective_lang = (language or conv.language or DEFAULT_LANGUAGE).strip().lower()
        if not is_language_supported(effective_lang):
            effective_lang = conv.language or DEFAULT_LANGUAGE
        if effective_lang != conv.language:
            conv.language = effective_lang

        # Validate and decode optional image
        image_info = image_handler.validate_and_decode(
            image_base64=image_base64,
            image_content_type=image_content_type,
            image_filename=image_filename,
            image_path=image_path,
        )
        file_bytes, mime_type, filename, image_metadata = (
            image_info if image_info else (None, None, None, None)
        )

        # 1. Assemble context BEFORE appending the current question to history
        assembled = await self.context_assembler.assemble(
            user_id=user_id,
            conversation_id=conversation_id,
            farmer_question=clean_q,
            image_metadata=image_metadata,
            image_bytes=file_bytes,
            image_mime_type=mime_type,
            image_filename=filename,
            language=effective_lang,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
        )

        # 2. Persist farmer question with attached image metadata if provided
        user_msg_context: Optional[dict] = None
        if image_metadata:
            user_msg_context = {
                "attached_image": image_metadata,
                "language": effective_lang,
            }
        elif effective_lang != DEFAULT_LANGUAGE:
            user_msg_context = {"language": effective_lang}

        user_msg = await self.advisory_repo.add_message(
            conversation_id=conversation_id,
            sender_role="user",
            message_text=clean_q,
            context_used=user_msg_context,
        )

        # 3. Provider Capability Check
        current_provider = self.router.get_provider()

        if image_metadata is not None and not current_provider.supports_images:
            # Configured provider does not support image understanding
            provider_result = AdvisoryProviderResult(
                content=(
                    f"The configured advisory provider ({current_provider.get_provider_name()}) "
                    "does not support image understanding. Your text question can be processed without an "
                    "image, or you may use FarmSathi's dedicated Disease Detection feature to scan crop leaves."
                ),
                status=AdvisoryProviderStatus.PROVIDER_UNAVAILABLE,
                provider_name=current_provider.get_provider_name(),
                error_message="Provider does not support image inputs.",
            )
        else:
            # 4. Formulate provider request
            system_instructions = self.safety_layer.build_system_instructions(language=effective_lang)
            prompt_req = AdvisoryPromptRequest(
                farmer_question=clean_q,
                system_instructions=system_instructions,
                context_text=assembled.formatted_prompt_context,
                conversation_history=assembled.conversation_history,
                language=effective_lang,
                image_bytes=file_bytes,
                image_mime_type=mime_type,
                image_filename=filename,
            )

            # 5. Route and generate provider result
            provider_result = await self.router.route_and_generate(prompt_req)

        # 6. Apply safety and agricultural response rules
        processed_text, disclaimers, final_status = self.safety_layer.post_process(
            farmer_question=clean_q,
            provider_result=provider_result,
            structured_context=assembled.structured_context,
        )

        # 7. Persist assistant message with ground-truth context metadata
        context_record = {
            "summary": assembled.context_summary,
            "data": assembled.structured_context,
            "disclaimers": disclaimers,
            "provider_name": provider_result.provider_name,
            "provider_status": final_status.value,
            "language": effective_lang,
        }

        assistant_msg = await self.advisory_repo.add_message(
            conversation_id=conversation_id,
            sender_role="assistant",
            message_text=processed_text,
            context_used=context_record,
        )

        # Update conversation timestamp
        conv.updated_at = datetime.now(timezone.utc)
        await self.session.flush()

        return AdvisoryExecutionResponse(
            conversation_id=conversation_id,
            user_message=AdvisoryMessageResponse.model_validate(user_msg),
            assistant_message=AdvisoryMessageResponse.model_validate(assistant_msg),
            provider_status=final_status,
            safety_disclaimers=disclaimers,
            context_summary=assembled.context_summary,
            provider_name=provider_result.provider_name,
        )

    async def get_user_conversations(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> List[AdvisoryConversationSummary]:
        """Returns paginated list of conversations belonging to the authenticated user."""
        conversations = await self.advisory_repo.get_by_user_id(
            user_id, skip=skip, limit=limit
        )
        summaries: List[AdvisoryConversationSummary] = []
        for c in conversations:
            summaries.append(
                AdvisoryConversationSummary(
                    id=c.id,
                    title=c.title,
                    language=c.language,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                    message_count=len(c.messages) if c.messages else 0,
                )
            )
        return summaries

    async def get_conversation_detail(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> AdvisoryConversationDetail:
        """Retrieves full conversation with messages, verifying user ownership."""
        conv = await self.advisory_repo.get_by_id_and_user_id(conversation_id, user_id)
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Advisory conversation not found or access denied.",
            )

        return AdvisoryConversationDetail(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            language=conv.language,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=[
                AdvisoryMessageResponse.model_validate(m) for m in conv.messages
            ],
        )

    async def delete_conversation(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Deletes conversation if owned by the user."""
        success = await self.advisory_repo.delete_conversation(conversation_id, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Advisory conversation not found or access denied.",
            )
        return True
