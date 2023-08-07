import sqlalchemy as sa
import functools as ft
from iatidatacube.extensions import db


act_ForeignKey = ft.partial(
    sa.ForeignKey,
    ondelete="CASCADE"
)

class ReportingOrganisation(db.Model):
    __tablename__="reporting_organisation"
    code = sa.Column(sa.UnicodeText, primary_key=True)
    type = sa.Column(sa.Integer, nullable=True, index=True)
    name_en = sa.Column(sa.UnicodeText,
        nullable=False)
    name_fr = sa.Column(sa.UnicodeText,
        nullable=False)
    name_es = sa.Column(sa.UnicodeText,
        nullable=False)
    name_pt = sa.Column(sa.UnicodeText,
        nullable=False)


class OrganisationType(db.Model):
    __tablename__= "organisation_type"
    code = sa.Column(sa.UnicodeText, primary_key=True)
    name_en = sa.Column(sa.UnicodeText,
        nullable=False)
    name_fr = sa.Column(sa.UnicodeText,
        nullable=False)
    name_es = sa.Column(sa.UnicodeText,
        nullable=False)
    name_pt = sa.Column(sa.UnicodeText,
        nullable=False)


class ProviderOrganisationType(db.Model):
    __tablename__= "provider_organisation_type"
    code = sa.Column(sa.UnicodeText, primary_key=True)
    name_en = sa.Column(sa.UnicodeText,
        nullable=False)
    name_fr = sa.Column(sa.UnicodeText,
        nullable=False)
    name_es = sa.Column(sa.UnicodeText,
        nullable=False)
    name_pt = sa.Column(sa.UnicodeText,
        nullable=False)


class ReceiverOrganisationType(db.Model):
    __tablename__= "receiver_organisation_type"
    code = sa.Column(sa.UnicodeText, primary_key=True)
    name_en = sa.Column(sa.UnicodeText,
        nullable=False)
    name_fr = sa.Column(sa.UnicodeText,
        nullable=False)
    name_es = sa.Column(sa.UnicodeText,
        nullable=False)
    name_pt = sa.Column(sa.UnicodeText,
        nullable=False)


class AidType(db.Model):
    __tablename__= "aid_type"
    code = sa.Column(sa.UnicodeText, primary_key=True)
    name_en = sa.Column(sa.UnicodeText,
        nullable=False)
    name_fr = sa.Column(sa.UnicodeText,
        nullable=False)
    name_es = sa.Column(sa.UnicodeText,
        nullable=False)
    name_pt = sa.Column(sa.UnicodeText,
        nullable=False)


class FinanceType(db.Model):
    __tablename__= "finance_type"
    code = sa.Column(sa.UnicodeText, primary_key=True)
    name_en = sa.Column(sa.UnicodeText,
        nullable=False)
    name_fr = sa.Column(sa.UnicodeText,
        nullable=False)
    name_es = sa.Column(sa.UnicodeText,
        nullable=False)
    name_pt = sa.Column(sa.UnicodeText,
        nullable=False)


class FlowType(db.Model):
    __tablename__= "flow_type"
    code = sa.Column(sa.UnicodeText, primary_key=True)
    name_en = sa.Column(sa.UnicodeText,
        nullable=False)
    name_fr = sa.Column(sa.UnicodeText,
        nullable=False)
    name_es = sa.Column(sa.UnicodeText,
        nullable=False)
    name_pt = sa.Column(sa.UnicodeText,
        nullable=False)


class TransactionType(db.Model):
    __tablename__= "transaction_type"
    code = sa.Column(sa.UnicodeText, primary_key=True)
    name_en = sa.Column(sa.UnicodeText,
        nullable=False)
    name_fr = sa.Column(sa.UnicodeText,
        nullable=False)
    name_es = sa.Column(sa.UnicodeText,
        nullable=False)
    name_pt = sa.Column(sa.UnicodeText,
        nullable=False)


class RecipientCountryorRegion(db.Model):
    __tablename__= "recipient_country_or_region"
    code = sa.Column(sa.UnicodeText, primary_key=True)
    name_en = sa.Column(sa.UnicodeText,
        nullable=False)
    name_fr = sa.Column(sa.UnicodeText,
        nullable=False)
    name_es = sa.Column(sa.UnicodeText,
        nullable=False)
    name_pt = sa.Column(sa.UnicodeText,
        nullable=False)


class SectorCategory(db.Model):
    __tablename__= "sector_category"
    code = sa.Column(sa.UnicodeText, primary_key=True)
    name_en = sa.Column(sa.UnicodeText,
        nullable=False)
    name_fr = sa.Column(sa.UnicodeText,
        nullable=False)
    name_es = sa.Column(sa.UnicodeText,
        nullable=False)
    name_pt = sa.Column(sa.UnicodeText,
        nullable=False)


class Sector(db.Model):
    __tablename__= "sector"
    code = sa.Column(sa.UnicodeText, primary_key=True)
    name_en = sa.Column(sa.UnicodeText,
        nullable=False)
    name_fr = sa.Column(sa.UnicodeText,
        nullable=False)
    name_es = sa.Column(sa.UnicodeText,
        nullable=False)
    name_pt = sa.Column(sa.UnicodeText,
        nullable=False)


class ReportingOrganisationGroup(db.Model):
    __tablename__= "reporting_organisation_group"
    code = sa.Column(sa.UnicodeText, primary_key=True)
    name_en = sa.Column(sa.UnicodeText,
        nullable=False)
    name_fr = sa.Column(sa.UnicodeText,
        nullable=False)
    name_es = sa.Column(sa.UnicodeText,
        nullable=False)
    name_pt = sa.Column(sa.UnicodeText,
        nullable=False)


class Dataset(db.Model):
    __tablename__="dataset"
    id = sa.Column(sa.UnicodeText, primary_key=True)
    dataset_type = sa.Column(sa.UnicodeText, nullable=False)
    country = sa.Column(sa.UnicodeText, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False, index=True)
    processing_at = sa.Column(sa.DateTime, nullable=False, index=True)
    updated_at = sa.Column(sa.DateTime, nullable=True, index=True)
    status = sa.Column(sa.Integer, nullable=False, index=True)


class IATIActivity(db.Model):
    __tablename__="iati_activity"
    iati_identifier = sa.Column(sa.UnicodeText, primary_key=True)
    title = sa.Column(sa.UnicodeText, nullable=False, index=True)
    title_fr = sa.Column(sa.UnicodeText, nullable=False, index=True)
    title_pt = sa.Column(sa.UnicodeText, nullable=False, index=True)
    title_es = sa.Column(sa.UnicodeText, nullable=False, index=True)
    description = sa.Column(sa.UnicodeText, nullable=False)
    description_fr = sa.Column(sa.UnicodeText, nullable=False)
    description_pt = sa.Column(sa.UnicodeText, nullable=False)
    description_es = sa.Column(sa.UnicodeText, nullable=False)
    start_date = sa.Column(sa.Date, nullable=True, index=True)
    end_date = sa.Column(sa.Date, nullable=True, index=True)
    glide = sa.Column(sa.UnicodeText, nullable=True, index=True)
    hrp = sa.Column(sa.UnicodeText, nullable=True, index=True)
    location = sa.Column(sa.UnicodeText, nullable=True)
    _hash = sa.Column(sa.UnicodeText, nullable=True, index=True)


class IATILine(db.Model):
    __tablename__="iati_line"
    id = sa.Column(sa.Integer, primary_key=True)
    iati_identifier = sa.Column(sa.UnicodeText,
        act_ForeignKey("iati_activity.iati_identifier"))
    reporting_organisation_group = sa.Column(
        sa.UnicodeText,
        act_ForeignKey("reporting_organisation_group.code"),
        nullable=False, index=True)
    reporting_organisation = sa.Column(
        sa.UnicodeText,
        act_ForeignKey("reporting_organisation.code"),
        nullable=False, index=True)
    reporting_organisation_type = sa.Column(
        sa.UnicodeText,
        act_ForeignKey("organisation_type.code"),
        nullable=False, index=True)
    aid_type = sa.Column(sa.UnicodeText,
        act_ForeignKey("aid_type.code"),
        nullable=True, index=True)
    finance_type = sa.Column(sa.UnicodeText,
        act_ForeignKey("finance_type.code"),
        nullable=True, index=True)
    flow_type = sa.Column(sa.UnicodeText,
        act_ForeignKey("flow_type.code"),
        nullable=True, index=True)
    provider_organisation = sa.Column(sa.UnicodeText,
        nullable=False, index=True)
    provider_organisation_fr = sa.Column(sa.UnicodeText,
        nullable=False, index=True)
    provider_organisation_pt = sa.Column(sa.UnicodeText,
        nullable=False, index=True)
    provider_organisation_es = sa.Column(sa.UnicodeText,
        nullable=False, index=True)
    provider_organisation_type = sa.Column(
        sa.UnicodeText,
        act_ForeignKey("provider_organisation_type.code"),
        nullable=True, index=True)
    receiver_organisation = sa.Column(sa.UnicodeText,
        nullable=False, index=True)
    receiver_organisation_fr = sa.Column(sa.UnicodeText,
        nullable=False, index=True)
    receiver_organisation_pt = sa.Column(sa.UnicodeText,
        nullable=False, index=True)
    receiver_organisation_es = sa.Column(sa.UnicodeText,
        nullable=False, index=True)
    receiver_organisation_type = sa.Column(
        sa.UnicodeText,
        act_ForeignKey("receiver_organisation_type.code"),
        nullable=True, index=True)
    transaction_type = sa.Column(sa.UnicodeText,
        act_ForeignKey("transaction_type.code"),
        nullable=True, index=True)
    recipient_country_or_region = sa.Column(sa.UnicodeText,
        act_ForeignKey("recipient_country_or_region.code"),
        nullable=True, index=True)
    multi_country = sa.Column(sa.Boolean,
        nullable=False, index=True)
    sector_category = sa.Column(sa.UnicodeText,
        act_ForeignKey("sector_category.code"),
        nullable=True, index=True)
    sector = sa.Column(sa.UnicodeText,
        act_ForeignKey("sector.code"),
        nullable=True, index=True)
    humanitarian = sa.Column(sa.Boolean,
        nullable=False, index=True)
    calendar_year = sa.Column(sa.UnicodeText,
        nullable=False, index=True)
    calendar_quarter = sa.Column(sa.UnicodeText,
        nullable=False, index=True)
    calendar_year_and_quarter = sa.Column(sa.UnicodeText,
        nullable=False, index=True)
    url = sa.Column(sa.UnicodeText, nullable=False)
    value_usd = sa.Column(sa.Float, nullable=False)
    value_eur = sa.Column(sa.Float, nullable=False)
    value_local_currrency = sa.Column(sa.Float, nullable=False)
