"""empty message

Revision ID: 67bda10c3cee
Revises: fc48f6d81d02
Create Date: 2023-08-07 20:03:36.111212

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67bda10c3cee'
down_revision = 'fc48f6d81d02'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('iati_line', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               type_=sa.UnicodeText(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('iati_line', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.UnicodeText(),
               type_=sa.INTEGER(),
               postgresql_using='id::integer',
               existing_nullable=False)

    # ### end Alembic commands ###
