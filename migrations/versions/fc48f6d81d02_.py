"""empty message

Revision ID: fc48f6d81d02
Revises: 75a6e15cb36b
Create Date: 2023-08-07 16:59:13.379969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc48f6d81d02'
down_revision = '75a6e15cb36b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('iati_activity', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_iati_activity_title'), [sa.text("left(title, 100)")], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_activity_title_es'), [sa.text("left(title_es, 100)")], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_activity_title_fr'), [sa.text("left(title_fr, 100)")], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_activity_title_pt'), [sa.text("left(title_pt, 100)")], unique=False)

    with op.batch_alter_table('iati_line', schema=None) as batch_op:
        batch_op.alter_column('reporting_organisation_group',
               existing_type=sa.TEXT(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('iati_line', schema=None) as batch_op:
        batch_op.alter_column('reporting_organisation_group',
               existing_type=sa.TEXT(),
               nullable=True)

    with op.batch_alter_table('iati_activity', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_iati_activity_title_pt'))
        batch_op.drop_index(batch_op.f('ix_iati_activity_title_fr'))
        batch_op.drop_index(batch_op.f('ix_iati_activity_title_es'))
        batch_op.drop_index(batch_op.f('ix_iati_activity_title'))

    # ### end Alembic commands ###
