"""empty message

Revision ID: 09adb777bee6
Revises: 67bda10c3cee
Create Date: 2023-08-07 20:37:54.814651

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09adb777bee6'
down_revision = '67bda10c3cee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('iati_activity', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reporting_organisation', sa.UnicodeText(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('iati_activity', schema=None) as batch_op:
        batch_op.drop_column('reporting_organisation')

    # ### end Alembic commands ###
