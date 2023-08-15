import os, json
from io import BytesIO

import pytest
import sqlalchemy as sa
from flask import url_for
import openpyxl

from iatidatacube import import_codelists, import_data, xlsx_to_csv
from iatidatacube.models import *


@pytest.mark.usefixtures('client_class')
class TestAPI:
    @pytest.fixture(autouse=True)
    def codelists_data(self):
        yield import_codelists.import_codelists()
        for table in [ReportingOrganisation, AidType,
        FinanceType, FlowType, TransactionType, Sector,
        OrganisationType, RecipientCountryorRegion,
        SectorCategory, ReportingOrganisationGroup]:
            db.session.execute(sa.delete(table))


    @pytest.fixture
    def codelists(self):
        yield {
            "reporting_organisation_group": [item.code for item in ReportingOrganisationGroup.query.all()],
            "reporting_organisation": [item.code for item in ReportingOrganisation.query.all()],
            "reporting_organisation_type": [item.code for item in OrganisationType.query.all()],
            "provider_organisation_type": [item.code for item in OrganisationType.query.all()],
            "receiver_organisation_type": [item.code for item in OrganisationType.query.all()],
            "aid_type": [item.code for item in AidType.query.all()],
            "finance_type": [item.code for item in FinanceType.query.all()],
            "flow_type": [item.code for item in FlowType.query.all()],
            "transaction_type": [item.code for item in TransactionType.query.all()],
            "sector_category": [item.code for item in SectorCategory.query.all()],
            "sector": [item.code for item in Sector.query.all()],
            "recipient_country_or_region": [item.code for item in RecipientCountryorRegion.query.all()]
        }


    @pytest.fixture
    def import_activities(self):
        yield import_data.import_activities(csv_file='44000.csv',
            force_update=False,
            directory=os.path.join('tests', 'fixtures', 'activities', 'csv'))
        for table in [IATILine, IATIActivity, ProviderOrganisation,
            ReceiverOrganisation]:
            db.session.execute(sa.delete(table))


    @pytest.fixture
    def import_transactions(self, codelists, import_activities):
        import_data.import_from_csv(csv_file='transaction-LR.csv',
            codelists=codelists,
            langs=['en', 'fr', 'es', 'pt'],
            directory=os.path.join('tests', 'fixtures', 'transactions', 'csv'))
        yield import_data.import_from_csv(csv_file='budget-LR.csv',
            codelists=codelists,
            langs=['en', 'fr', 'es', 'pt'],
            directory=os.path.join('tests', 'fixtures', 'transactions', 'csv'))
        for table in [IATILine, ProviderOrganisation,
            ReceiverOrganisation]:
            db.session.execute(sa.delete(table))


    def test_get_drilldowns(self, import_transactions, client):
        res = client.get(url_for('babbage_api.aggregate', name='iatiline',
            drilldown='recipient_country_or_region'))
        assert len(res.json['cells']) == 1, res.json
        assert int(res.json['cells'][0]['value_usd.sum']) == 174739435, res.json['cells'][0]


    def test_get_drilldowns_rollups(self, import_transactions, client):
        res = client.get(url_for('babbage_api.aggregate', name='iatiline',
            drilldown='recipient_country_or_region',
            rollup='transaction_type.code:[["budget"],["3","4"]]'))
        assert len(res.json['cells']) == 1, res.json
        assert round(res.json['cells'][0]['value_usd.sum_3-4']) == 58742699, res.json['cells'][0]
        assert round(res.json['cells'][0]['value_usd.sum_budget']) == 58000000, res.json['cells'][0]


    def test_get_drilldowns_xlsx(self, import_transactions, client):
        res = client.get(url_for('babbage_api.aggregate', name='iatiline',
            drilldown='recipient_country_or_region', format='xlsx', lang='fr'))
        xlsx_res = res.get_data()
        xlsx_as_csv = xlsx_to_csv.get_data(xlsx_res, xlsx_res, 'Data')
        assert list(xlsx_as_csv[0].keys()) == ['Pays ou région bénéficiaire',
        'Value (USD)']


    def test_get_drilldowns_rollups_xlsx(self, import_transactions, client):
        res = client.get(url_for('babbage_api.aggregate', name='iatiline',
            drilldown='recipient_country_or_region',
            rollup='transaction_type.code:[["budget"],["3","4"]]',
            format='xlsx', lang='fr'))
        xlsx_res = res.get_data()
        xlsx_as_csv = xlsx_to_csv.get_data(xlsx_res, xlsx_res, 'Data')
        assert list(xlsx_as_csv[0].keys()) == ['Pays ou région bénéficiaire',
        'Value (USD) (Budget)', 'Value (USD) (Décaissement, Dépenses)']
        assert xlsx_as_csv[0]['Value (USD) (Décaissement, Dépenses)'] == 58742699
        assert xlsx_as_csv[0]['Value (USD) (Budget)'] == 58000000

