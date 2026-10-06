from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.advisory import AdvisoryConversation, AdvisoryMessage
from app.repositories.base import BaseRepository


class AdvisoryRepository(BaseRepository[AdvisoryConversation]):
    def __init__(self, session: AsyncSession):
        super().__init__(AdvisoryConversation, session)

    async def get_with_messages(
        self, conversation_id
    ) -> Optional[AdvisoryConversation]:
        result = await self.session.execute(
            select(AdvisoryConversation)
            .options(selectinload(AdvisoryConversation.messages))
            .where(AdvisoryConversation.id == conversation_id)
            .execution_options(populate_existing=True)
        )
        return result.scalars().first()

    async def get_by_user_id(
        self, user_id, skip: int = 0, limit: int = 20
    ) -> List[AdvisoryConversation]:
        result = await self.session.execute(
            select(AdvisoryConversation)
            .options(selectinload(AdvisoryConversation.messages))
            .where(AdvisoryConversation.user_id == user_id)
            .order_by(AdvisoryConversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .execution_options(populate_existing=True)
        )
        return list(result.scalars().all())

    async def count_by_user_id(self, user_id) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(AdvisoryConversation).where(
                AdvisoryConversation.user_id == user_id
            )
        )
        return result.scalar() or 0

    async def create_conversation(
        self, user_id, title: str, language: str = "en"
    ) -> AdvisoryConversation:
        conv = AdvisoryConversation(
            user_id=user_id,
            title=title,
            language=language,
        )
        self.session.add(conv)
        await self.session.flush()
        await self.session.refresh(conv)
        return conv

    async def get_by_id_and_user_id(
        self, conversation_id, user_id
    ) -> Optional[AdvisoryConversation]:
        result = await self.session.execute(
            select(AdvisoryConversation)
            .options(selectinload(AdvisoryConversation.messages))
            .where(
                AdvisoryConversation.id == conversation_id,
                AdvisoryConversation.user_id == user_id,
            )
            .execution_options(populate_existing=True)
        )
        return result.scalars().first()

    async def delete_conversation(self, conversation_id, user_id) -> bool:
        conv = await self.get_by_id_and_user_id(conversation_id, user_id)
        if not conv:
            return False
        await self.session.delete(conv)
        await self.session.flush()
        return True

    async def add_message(
        self,
        conversation_id,
        sender_role: str,
        message_text: str,
        audio_path: Optional[str] = None,
        context_used: Optional[dict] = None,
    ) -> AdvisoryMessage:
        msg = AdvisoryMessage(
            conversation_id=conversation_id,
            sender_role=sender_role,
            message_text=message_text,
            audio_path=audio_path,
            context_used=context_used,
        )
        self.session.add(msg)
        await self.session.flush()
        await self.session.refresh(msg)
        return msg

