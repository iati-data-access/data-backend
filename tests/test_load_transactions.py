import os
import csv

import pytest
import sqlalchemy as sa

from iatidatacube import import_codelists
from iatidatacube import import_data
from iatidatacube.models import *


@pytest.mark.usefixtures('client_class')
class TestLoadData:
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
        yield import_data.import_from_csv(csv_file='transaction-LR.csv',
            codelists=codelists,
            langs=['en', 'fr', 'es', 'pt'],
            directory=os.path.join('tests', 'fixtures', 'transactions', 'csv'))
        for table in [IATILine, ProviderOrganisation,
            ReceiverOrganisation]:
            db.session.execute(sa.delete(table))


    @pytest.fixture
    def import_budgets(self, codelists, import_activities):
        yield import_data.import_from_csv(csv_file='budget-LR.csv',
            codelists=codelists,
            langs=['en', 'fr', 'es', 'pt'],
            directory=os.path.join('tests', 'fixtures', 'transactions', 'csv'))
        for table in [IATILine, ProviderOrganisation,
            ReceiverOrganisation]:
            db.session.execute(sa.delete(table))


    def test_dataframe_length(self):
        """There should be 139 transactions."""
        df = import_data.get_dataframe(csv_file='transaction-LR.csv',
            langs=['en', 'fr', 'es', 'pt'],
            directory=os.path.join('tests', 'fixtures', 'transactions', 'csv'))
        rows = df.to_dict(orient='records')
        assert len(rows) == 139


    def test_transactions_loaded(self, import_transactions):
        """There should be 139 transactions - same as in the dataframe."""
        lines = IATILine.query.all()
        assert len(lines) == 139


    def test_budget_dataframe_length(self):
        """There should be 161 transactions."""
        df = import_data.get_dataframe(csv_file='budget-LR.csv',
            langs=['en', 'fr', 'es', 'pt'],
            directory=os.path.join('tests', 'fixtures', 'transactions', 'csv'))
        rows = df.to_dict(orient='records')
        assert len(rows) == 161


    def test_budgets_loaded(self, import_budgets):
        """There should be 161 transactions -- same as in the dataframe."""
        lines = IATILine.query.all()
        assert len(lines) == 161


    def test_transactions_deleted(self, import_transactions, codelists):
        """Test that transactions get removed when they are no longer in the dataset."""
        lines = IATILine.query.all()
        assert len(lines) == 139
        df = import_data.import_from_csv(csv_file='transaction-LR.csv',
            codelists=codelists,
            langs=['en', 'fr', 'es', 'pt'],
            directory=os.path.join('tests', 'fixtures', 'transactions', 'csv_delete'))
        lines = IATILine.query.all()
        assert len(lines) == 138


    def _test_filter_transactions(self):
        """Wrote this to quickly filter a larger dataset to create a more manageable one"""
        with open(os.path.join('tests', 'fixtures', 'transactions', 'budget-LR.csv')) as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            iati_identifiers = ['44000-P104716', '44000-P105683']
            transactions = list(filter(lambda row: row['iati_identifier'] in iati_identifiers, reader))

        with open(os.path.join('tests', 'fixtures', 'transactions', 'budget-LR-small.csv'), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in transactions:
                writer.writerow(row)
