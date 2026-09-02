"""persist shared, versioned AI impact predictor results"""

from alembic import op
import sqlalchemy as sa

revision = "005_impact_prediction_records"
down_revision = "004_chat_conversations"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "impact_prediction_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("issue_id", sa.Integer(), sa.ForeignKey("issues.id"), nullable=False),
        sa.Column("signature", sa.String(64), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_impact_prediction_records_issue_id", "impact_prediction_records", ["issue_id"], unique=True)


def downgrade():
    op.drop_index("ix_impact_prediction_records_issue_id", table_name="impact_prediction_records")
    op.drop_table("impact_prediction_records")
