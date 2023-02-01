"""empty message

Revision ID: 0d2888ebd30d
Revises: 39b56c7ddfce
Create Date: 2023-02-01 17:57:41.632542

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d2888ebd30d'
down_revision = '39b56c7ddfce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('iati_activity', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.UnicodeText(), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('description_fr', sa.UnicodeText(), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('description_pt', sa.UnicodeText(), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('description_es', sa.UnicodeText(), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('start_date', sa.Date(), nullable=True, index=True))
        batch_op.add_column(sa.Column('end_date', sa.Date(), nullable=True, index=True))
        batch_op.add_column(sa.Column('glide', sa.UnicodeText(), nullable=True, index=True))
        batch_op.add_column(sa.Column('hrp', sa.UnicodeText(), nullable=True, index=True))
        batch_op.add_column(sa.Column('location', sa.UnicodeText(), nullable=True, index=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('iati_activity', schema=None) as batch_op:
        batch_op.drop_column('location')
        batch_op.drop_column('hrp')
        batch_op.drop_column('glide')
        batch_op.drop_column('end_date')
        batch_op.drop_column('start_date')
        batch_op.drop_column('description_es')
        batch_op.drop_column('description_pt')
        batch_op.drop_column('description_fr')
        batch_op.drop_column('description')

    # ### end Alembic commands ###