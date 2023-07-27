"""empty message

Revision ID: 37b6935fa9ce
Revises: 
Create Date: 2023-07-27 22:43:54.683358

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37b6935fa9ce'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('aid_type',
    sa.Column('code', sa.UnicodeText(), nullable=False),
    sa.Column('name_en', sa.UnicodeText(), nullable=False),
    sa.Column('name_fr', sa.UnicodeText(), nullable=False),
    sa.Column('name_es', sa.UnicodeText(), nullable=False),
    sa.Column('name_pt', sa.UnicodeText(), nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_table('finance_type',
    sa.Column('code', sa.UnicodeText(), nullable=False),
    sa.Column('name_en', sa.UnicodeText(), nullable=False),
    sa.Column('name_fr', sa.UnicodeText(), nullable=False),
    sa.Column('name_es', sa.UnicodeText(), nullable=False),
    sa.Column('name_pt', sa.UnicodeText(), nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_table('flow_type',
    sa.Column('code', sa.UnicodeText(), nullable=False),
    sa.Column('name_en', sa.UnicodeText(), nullable=False),
    sa.Column('name_fr', sa.UnicodeText(), nullable=False),
    sa.Column('name_es', sa.UnicodeText(), nullable=False),
    sa.Column('name_pt', sa.UnicodeText(), nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_table('iati_activity',
    sa.Column('iati_identifier', sa.UnicodeText(), nullable=False),
    sa.Column('title', sa.UnicodeText(), nullable=False),
    sa.PrimaryKeyConstraint('iati_identifier')
    )
    op.create_table('organisation_type',
    sa.Column('code', sa.UnicodeText(), nullable=False),
    sa.Column('name_en', sa.UnicodeText(), nullable=False),
    sa.Column('name_fr', sa.UnicodeText(), nullable=False),
    sa.Column('name_es', sa.UnicodeText(), nullable=False),
    sa.Column('name_pt', sa.UnicodeText(), nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_table('recipient_country_or_region',
    sa.Column('code', sa.UnicodeText(), nullable=False),
    sa.Column('name_en', sa.UnicodeText(), nullable=False),
    sa.Column('name_fr', sa.UnicodeText(), nullable=False),
    sa.Column('name_es', sa.UnicodeText(), nullable=False),
    sa.Column('name_pt', sa.UnicodeText(), nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_table('reporting_organisation',
    sa.Column('code', sa.UnicodeText(), nullable=False),
    sa.Column('type', sa.Integer(), nullable=True),
    sa.Column('name_en', sa.UnicodeText(), nullable=False),
    sa.Column('name_fr', sa.UnicodeText(), nullable=False),
    sa.Column('name_es', sa.UnicodeText(), nullable=False),
    sa.Column('name_pt', sa.UnicodeText(), nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    with op.batch_alter_table('reporting_organisation', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_reporting_organisation_type'), ['type'], unique=False)

    op.create_table('sector',
    sa.Column('code', sa.UnicodeText(), nullable=False),
    sa.Column('name_en', sa.UnicodeText(), nullable=False),
    sa.Column('name_fr', sa.UnicodeText(), nullable=False),
    sa.Column('name_es', sa.UnicodeText(), nullable=False),
    sa.Column('name_pt', sa.UnicodeText(), nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_table('sector_category',
    sa.Column('code', sa.UnicodeText(), nullable=False),
    sa.Column('name_en', sa.UnicodeText(), nullable=False),
    sa.Column('name_fr', sa.UnicodeText(), nullable=False),
    sa.Column('name_es', sa.UnicodeText(), nullable=False),
    sa.Column('name_pt', sa.UnicodeText(), nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_table('transaction_type',
    sa.Column('code', sa.UnicodeText(), nullable=False),
    sa.Column('name_en', sa.UnicodeText(), nullable=False),
    sa.Column('name_fr', sa.UnicodeText(), nullable=False),
    sa.Column('name_es', sa.UnicodeText(), nullable=False),
    sa.Column('name_pt', sa.UnicodeText(), nullable=False),
    sa.PrimaryKeyConstraint('code')
    )
    op.create_table('iati_line',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('iati_identifier', sa.UnicodeText(), nullable=True),
    sa.Column('reporting_organisation', sa.UnicodeText(), nullable=False),
    sa.Column('reporting_organisation_type', sa.UnicodeText(), nullable=False),
    sa.Column('aid_type', sa.UnicodeText(), nullable=True),
    sa.Column('finance_type', sa.UnicodeText(), nullable=True),
    sa.Column('flow_type', sa.UnicodeText(), nullable=True),
    sa.Column('provider_organisation', sa.UnicodeText(), nullable=False),
    sa.Column('provider_organisation_type', sa.UnicodeText(), nullable=True),
    sa.Column('receiver_organisation', sa.UnicodeText(), nullable=False),
    sa.Column('receiver_organisation_type', sa.UnicodeText(), nullable=True),
    sa.Column('transaction_type', sa.UnicodeText(), nullable=True),
    sa.Column('recipient_country_or_region', sa.UnicodeText(), nullable=True),
    sa.Column('multi_country', sa.Boolean(), nullable=False),
    sa.Column('sector_category', sa.UnicodeText(), nullable=True),
    sa.Column('sector', sa.UnicodeText(), nullable=True),
    sa.Column('humanitarian', sa.Boolean(), nullable=False),
    sa.Column('calendar_year', sa.UnicodeText(), nullable=False),
    sa.Column('calendar_quarter', sa.UnicodeText(), nullable=False),
    sa.Column('calendar_year_and_quarter', sa.UnicodeText(), nullable=False),
    sa.Column('url', sa.UnicodeText(), nullable=False),
    sa.Column('value_usd', sa.Float(), nullable=False),
    sa.Column('value_eur', sa.Float(), nullable=False),
    sa.Column('value_local_currrency', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['aid_type'], ['aid_type.code'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['finance_type'], ['finance_type.code'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['flow_type'], ['flow_type.code'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['iati_identifier'], ['iati_activity.iati_identifier'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['recipient_country_or_region'], ['recipient_country_or_region.code'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reporting_organisation'], ['reporting_organisation.code'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reporting_organisation_type'], ['organisation_type.code'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['sector'], ['sector.code'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['sector_category'], ['sector_category.code'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['transaction_type'], ['transaction_type.code'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('iati_line', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_iati_line_aid_type'), ['aid_type'], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_line_calendar_quarter'), ['calendar_quarter'], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_line_calendar_year'), ['calendar_year'], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_line_calendar_year_and_quarter'), ['calendar_year_and_quarter'], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_line_finance_type'), ['finance_type'], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_line_flow_type'), ['flow_type'], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_line_humanitarian'), ['humanitarian'], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_line_multi_country'), ['multi_country'], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_line_recipient_country_or_region'), ['recipient_country_or_region'], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_line_reporting_organisation'), ['reporting_organisation'], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_line_reporting_organisation_type'), ['reporting_organisation_type'], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_line_sector'), ['sector'], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_line_sector_category'), ['sector_category'], unique=False)
        batch_op.create_index(batch_op.f('ix_iati_line_transaction_type'), ['transaction_type'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('iati_line', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_iati_line_transaction_type'))
        batch_op.drop_index(batch_op.f('ix_iati_line_sector_category'))
        batch_op.drop_index(batch_op.f('ix_iati_line_sector'))
        batch_op.drop_index(batch_op.f('ix_iati_line_reporting_organisation_type'))
        batch_op.drop_index(batch_op.f('ix_iati_line_reporting_organisation'))
        batch_op.drop_index(batch_op.f('ix_iati_line_recipient_country_or_region'))
        batch_op.drop_index(batch_op.f('ix_iati_line_multi_country'))
        batch_op.drop_index(batch_op.f('ix_iati_line_humanitarian'))
        batch_op.drop_index(batch_op.f('ix_iati_line_flow_type'))
        batch_op.drop_index(batch_op.f('ix_iati_line_finance_type'))
        batch_op.drop_index(batch_op.f('ix_iati_line_calendar_year_and_quarter'))
        batch_op.drop_index(batch_op.f('ix_iati_line_calendar_year'))
        batch_op.drop_index(batch_op.f('ix_iati_line_calendar_quarter'))
        batch_op.drop_index(batch_op.f('ix_iati_line_aid_type'))

    op.drop_table('iati_line')
    op.drop_table('transaction_type')
    op.drop_table('sector_category')
    op.drop_table('sector')
    with op.batch_alter_table('reporting_organisation', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_reporting_organisation_type'))

    op.drop_table('reporting_organisation')
    op.drop_table('recipient_country_or_region')
    op.drop_table('organisation_type')
    op.drop_table('iati_activity')
    op.drop_table('flow_type')
    op.drop_table('finance_type')
    op.drop_table('aid_type')
    # ### end Alembic commands ###
