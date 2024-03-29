"""empty message

Revision ID: 7d9e7b5c1d64
Revises: 0d2888ebd30d
Create Date: 2023-02-01 19:14:30.560273

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d9e7b5c1d64'
down_revision = '0d2888ebd30d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dataset',
    sa.Column('id', sa.UnicodeText(), nullable=False),
    sa.Column('dataset_type', sa.UnicodeText(), nullable=False),
    sa.Column('country', sa.UnicodeText(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('processing_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('dataset', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_dataset_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_dataset_processing_at'), ['processing_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_dataset_status'), ['status'], unique=False)
        batch_op.create_index(batch_op.f('ix_dataset_updated_at'), ['updated_at'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('dataset', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_dataset_updated_at'))
        batch_op.drop_index(batch_op.f('ix_dataset_status'))
        batch_op.drop_index(batch_op.f('ix_dataset_processing_at'))
        batch_op.drop_index(batch_op.f('ix_dataset_created_at'))

    op.drop_table('dataset')
    # ### end Alembic commands ###
