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
        yield import_data.import_activities_from_single_csv(csv_file='44000.csv',
                                                            force_update=False,
                                                            directory=os.path.join('tests', 'fixtures', 'activities', 'csv'))
        for table in [IATILine, IATIActivity, ProviderOrganisation,
            ReceiverOrganisation]:
            db.session.execute(sa.delete(table))


    @pytest.fixture
    def import_transactions(self, codelists, import_activities):
        import_data.import_budgets_transactions_from_single_csv(csv_file='transaction-LR.csv',
                                                                codelists=codelists,
                                                                langs=['en', 'fr', 'es', 'pt'],
                                                                directory=os.path.join('tests', 'fixtures', 'transactions', 'csv'))
        yield import_data.import_budgets_transactions_from_single_csv(csv_file='budget-LR.csv',
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


    def test_get_drilldowns_empty_cut(self, import_transactions, client):
        """
        All the WB transactions have no provider organisation.
        All the WB budgets have provider organisation 40.
        """
        res = client.get(url_for('babbage_api.aggregate', name='iatiline',
            drilldown='recipient_country_or_region',
            cut='provider_organisation_type.code:""'))
        assert len(res.json['cells']) == 1, res.json
        assert int(res.json['cells'][0]['value_usd.sum']) == 116739436, res.json
        res = client.get(url_for('babbage_api.aggregate', name='iatiline',
            drilldown='recipient_country_or_region',
            cut='provider_organisation_type.code:"40"'))
        assert len(res.json['cells']) == 1, res.json
        assert int(res.json['cells'][0]['value_usd.sum']) == 58000000, res.json


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


    def test_get_drilldowns_rollups_xlsx_quarters(self, import_transactions, client):
        res = client.get(url_for('babbage_api.aggregate', name='iatiline',
            drilldown='recipient_country_or_region',
            cut='transaction_type.code:"3";"4"|calendar_year_and_quarter:"2013 Q1";"2013 Q2"',
            rollup='calendar_year_and_quarter:[["2013 Q1"],["2013 Q2"]]',
            aggregates='value_usd.sum',
            format='xlsx', lang='en'))
        xlsx_res = res.get_data()
        xlsx_as_csv = xlsx_to_csv.get_data(xlsx_res, xlsx_res, 'Data')
        assert list(xlsx_as_csv[0].keys()) == ['Recipient Country or Region',
        'Value (USD) (2013 Q1)', 'Value (USD) (2013 Q2)']
        assert xlsx_as_csv[0]['Value (USD) (2013 Q1)'] == 1984341
        assert xlsx_as_csv[0]['Value (USD) (2013 Q2)'] == 595716


    @pytest.mark.parametrize("rollup_name,rollup_values", [
        ("sector_category.code", ["120","150","160","310","430"]),
        ("sector.code", ["12220","15170","16010","31120","43040"]),
        ("year.year", ["2007","2008","2009","2010","2011","2012","2013","2014","2015"]),
        ("quarter.quarter", ["Q1","Q2","Q3","Q4"]),
        ("calendar_year_and_quarter", ["2013 Q1","2013 Q2","2013 Q3","2013 Q4"]),
        ])
    def test_get_drilldowns_rollups_various(self, import_transactions, client, rollup_name, rollup_values):
        rollup_values_cuts = ";".join([f'"{v}"' for v in rollup_values])
        rollup_values_rollups = ",".join([f'["{v}"]' for v in rollup_values])

        res = client.get(url_for('babbage_api.aggregate', name='iatiline',
            drilldown='recipient_country_or_region',
            cut=f'transaction_type.code:"3";"4"|{rollup_name}:{rollup_values_cuts}',
            rollup=f'{rollup_name}:[{rollup_values_rollups}]',
            aggregates='value_usd.sum',
            format='xlsx', lang='en'))
        assert res.status_code == 200


    def test_get_empty_xlsx(self, import_transactions, client):
        res = client.get(url_for('babbage_api.aggregate', name='iatiline',
            drilldown='recipient_country_or_region',
            cut='transaction_type.code:"3";"4"|calendar_year_and_quarter:"9999 Q1"',
            aggregates='value_usd.sum',
            format='xlsx', lang='en'))
        assert res.status_code == 404
