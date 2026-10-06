"""Initial normalized schema for FarmSathi

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 2. farmer_profiles table
    op.create_table(
        "farmer_profiles",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("preferred_language", sa.String(length=10), nullable=False, server_default="en"),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("district", sa.String(length=100), nullable=True),
        sa.Column("village", sa.String(length=100), nullable=True),
        sa.Column("latitude", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("land_size_acres", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column("soil_type", sa.String(length=50), nullable=True),
        sa.Column("irrigation_source", sa.String(length=50), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 3. crop_recommendations table
    op.create_table(
        "crop_recommendations",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("nitrogen", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("phosphorus", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("potassium", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("temperature", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("humidity", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("ph", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("rainfall", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("recommended_crop", sa.String(length=50), nullable=False),
        sa.Column("top_predictions", sa.JSON(), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_crop_recommendations_user_id", "crop_recommendations", ["user_id"])
    op.create_index("ix_crop_recommendations_created_at", "crop_recommendations", ["created_at"])

    # 4. disease_diagnoses table
    op.create_table(
        "disease_diagnoses",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("original_image_path", sa.String(length=500), nullable=False),
        sa.Column("predicted_condition", sa.String(length=100), nullable=True),
        sa.Column("confidence", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("is_confident", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("management_guidance", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_disease_diagnoses_user_id", "disease_diagnoses", ["user_id"])
    op.create_index("ix_disease_diagnoses_created_at", "disease_diagnoses", ["created_at"])

    # 5. advisory_conversations table
    op.create_table(
        "advisory_conversations",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("language", sa.String(length=10), nullable=False, server_default="en"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_advisory_conversations_user_id", "advisory_conversations", ["user_id"])

    # 6. advisory_messages table
    op.create_table(
        "advisory_messages",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", sa.Uuid(as_uuid=True), sa.ForeignKey("advisory_conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_role", sa.String(length=20), nullable=False),
        sa.Column("message_text", sa.Text(), nullable=False),
        sa.Column("audio_path", sa.String(length=500), nullable=True),
        sa.Column("context_used", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_advisory_messages_conversation_id", "advisory_messages", ["conversation_id"])

    # 7. weather_cache table
    op.create_table(
        "weather_cache",
        sa.Column("cache_key", sa.String(length=100), primary_key=True),
        sa.Column("latitude", sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column("longitude", sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column("current_conditions", sa.JSON(), nullable=False),
        sa.Column("forecast_daily", sa.JSON(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_weather_cache_expires_at", "weather_cache", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_weather_cache_expires_at", table_name="weather_cache")
    op.drop_table("weather_cache")

    op.drop_index("ix_advisory_messages_conversation_id", table_name="advisory_messages")
    op.drop_table("advisory_messages")

    op.drop_index("ix_advisory_conversations_user_id", table_name="advisory_conversations")
    op.drop_table("advisory_conversations")

    op.drop_index("ix_disease_diagnoses_created_at", table_name="disease_diagnoses")
    op.drop_index("ix_disease_diagnoses_user_id", table_name="disease_diagnoses")
    op.drop_table("disease_diagnoses")

    op.drop_index("ix_crop_recommendations_created_at", table_name="crop_recommendations")
    op.drop_index("ix_crop_recommendations_user_id", table_name="crop_recommendations")
    op.drop_table("crop_recommendations")

    op.drop_table("farmer_profiles")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_phone", table_name="users")
    op.drop_table("users")
