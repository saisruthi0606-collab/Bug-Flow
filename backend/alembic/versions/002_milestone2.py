"""milestone 2 issue collaboration and planning"""
from alembic import op
import sqlalchemy as sa
revision = '002_milestone2'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('sprints', sa.Column('id',sa.Integer(),primary_key=True), sa.Column('name',sa.String(255),nullable=False), sa.Column('goal',sa.Text()), sa.Column('start_date',sa.Date(),nullable=False), sa.Column('end_date',sa.Date(),nullable=False), sa.Column('status',sa.String(50),nullable=False), sa.Column('project_id',sa.Integer(),sa.ForeignKey('projects.id'),nullable=False), sa.Column('created_by',sa.Integer(),sa.ForeignKey('users.id'),nullable=False), sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.text('(CURRENT_TIMESTAMP)'),nullable=False))
    with op.batch_alter_table('issues') as batch:
        batch.add_column(sa.Column('category', sa.String(length=100), nullable=True))
        batch.add_column(sa.Column('sprint_id', sa.Integer(), nullable=True))
        batch.add_column(sa.Column('embedding', sa.Text(), nullable=True))
        batch.add_column(sa.Column('is_possible_duplicate', sa.Boolean(), nullable=False, server_default=sa.false()))
        batch.add_column(sa.Column('duplicate_of_issue_id', sa.Integer(), nullable=True))
    op.create_table('comments', sa.Column('id',sa.Integer(),primary_key=True),sa.Column('issue_id',sa.Integer(),sa.ForeignKey('issues.id'),nullable=False),sa.Column('author_id',sa.Integer(),sa.ForeignKey('users.id'),nullable=False),sa.Column('body',sa.Text(),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.text('(CURRENT_TIMESTAMP)'),nullable=False),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.text('(CURRENT_TIMESTAMP)'),nullable=False))
    op.create_table('attachments', sa.Column('id',sa.Integer(),primary_key=True),sa.Column('issue_id',sa.Integer(),sa.ForeignKey('issues.id'),nullable=False),sa.Column('uploaded_by',sa.Integer(),sa.ForeignKey('users.id'),nullable=False),sa.Column('original_filename',sa.String(255),nullable=False),sa.Column('stored_filename',sa.String(255),nullable=False,unique=True),sa.Column('content_type',sa.String(100)),sa.Column('size_bytes',sa.Integer(),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.text('(CURRENT_TIMESTAMP)'),nullable=False))
    op.create_table('activities', sa.Column('id',sa.Integer(),primary_key=True),sa.Column('issue_id',sa.Integer(),sa.ForeignKey('issues.id'),nullable=False),sa.Column('actor_id',sa.Integer(),sa.ForeignKey('users.id')),sa.Column('action',sa.String(100),nullable=False),sa.Column('details',sa.Text()),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.text('(CURRENT_TIMESTAMP)'),nullable=False))
    op.create_table('ai_recommendations', sa.Column('id',sa.Integer(),primary_key=True),sa.Column('issue_id',sa.Integer(),sa.ForeignKey('issues.id'),nullable=False,unique=True),sa.Column('category',sa.String(100)),sa.Column('severity',sa.String(50)),sa.Column('priority',sa.String(50)),sa.Column('root_cause',sa.Text()),sa.Column('suggested_resolution',sa.Text()),sa.Column('confidence_score',sa.Integer(),nullable=False),sa.Column('reasoning',sa.Text()),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.text('(CURRENT_TIMESTAMP)'),nullable=False))
def downgrade():
    op.drop_table('ai_recommendations'); op.drop_table('activities'); op.drop_table('attachments'); op.drop_table('comments'); op.drop_table('sprints')
    with op.batch_alter_table('issues') as batch:
        batch.drop_column('duplicate_of_issue_id'); batch.drop_column('is_possible_duplicate'); batch.drop_column('embedding'); batch.drop_column('sprint_id'); batch.drop_column('category')

