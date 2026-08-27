"""add optional conversation identifiers to chat history"""

from alembic import op
import sqlalchemy as sa


revision = "004_chat_conversations"
down_revision = "003_milestone3_ai"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("chat_messages", sa.Column("conversation_id", sa.String(length=100), nullable=True))
    op.create_index("ix_chat_messages_conversation_id", "chat_messages", ["conversation_id"])


def downgrade():
    op.drop_index("ix_chat_messages_conversation_id", table_name="chat_messages")
    op.drop_column("chat_messages", "conversation_id")
