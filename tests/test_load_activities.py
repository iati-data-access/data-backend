import csv
import os, json

import pytest
import sqlalchemy as sa

from iatidatacube import import_codelists
from iatidatacube import import_data
from iatidatacube.models import *


@pytest.mark.usefixtures('client_class')
class TestLoadData:
    @pytest.fixture
    def codelists_data(self):
        yield import_codelists.import_codelists()
        for table in [ReportingOrganisation, AidType,
        FinanceType, FlowType, TransactionType, Sector,
        OrganisationType, RecipientCountryorRegion,
        SectorCategory, ReportingOrganisationGroup]:
            db.session.execute(sa.delete(table))

    @pytest.fixture
    def import_activities(self, codelists_data):
        yield import_data.import_activities_from_single_csv(csv_file='44000.csv',
                                                            force_update=False,
                                                            directory=os.path.join('tests', 'fixtures', 'activities', 'csv'))
        for table in [IATILine, IATIActivity, ProviderOrganisation,
            ReceiverOrganisation]:
            db.session.execute(sa.delete(table))


    @pytest.fixture
    def import_activities_long_field(self):
        yield import_data.import_activities_from_single_csv(csv_file='XM-DAC-41317.csv',
                                                            force_update=False,
                                                            directory=os.path.join('tests', 'fixtures', 'activities', 'csv_long_field'))
        for table in [IATILine, IATIActivity, ProviderOrganisation,
            ReceiverOrganisation]:
            db.session.execute(sa.delete(table))


    def test_activities_loaded(self, import_activities):
        """There should be two activities"""
        activities = IATIActivity.query.all()
        assert len(activities) == 2


    def test_activities_updated(self, import_activities):
        """Update should update only if the hash has not changed"""
        activity = IATIActivity.query.filter_by(
            iati_identifier='44000-P104716').first()
        assert activity.title == 'LR-Agriculture & Infrastructure Development  Project'
        import_data.import_activities_from_single_csv(csv_file='44000.csv',
                                                      force_update=False,
                                                      directory=os.path.join('tests', 'fixtures', 'activities', 'csv_update'))
        activity = IATIActivity.query.filter_by(
            iati_identifier='44000-P104716').first()
        assert activity.title == 'UPDATED-LR-Agriculture & Infrastructure Development  Project'


    def test_activities_force_updated(self, import_activities):
        """Force update should update even if the hash has not changed"""
        activity = IATIActivity.query.filter_by(
            iati_identifier='44000-P104716').first()
        assert activity.title == 'LR-Agriculture & Infrastructure Development  Project'
        import_data.import_activities_from_single_csv(csv_file='44000.csv',
                                                      force_update=True,
                                                      directory=os.path.join('tests', 'fixtures', 'activities', 'csv_update_force'))
        activity = IATIActivity.query.filter_by(
            iati_identifier='44000-P104716').first()
        assert activity.title == 'FORCE-UPDATE-LR-Agriculture & Infrastructure Development  Project'


    def test_activities_deleted(self, import_activities):
        """Activities should be deleted if they are no longer in the source dataset"""
        activity = IATIActivity.query.filter_by(
            iati_identifier='44000-P104716').first()
        assert activity is not None
        import_data.import_activities_from_single_csv(csv_file='44000.csv',
                                                      force_update=True,
                                                      directory=os.path.join('tests', 'fixtures', 'activities', 'csv_delete'))
        activity = IATIActivity.query.filter_by(
            iati_identifier='44000-P104716').first()
        assert activity is None
        activities = IATIActivity.query.all()
        assert len(activities) == 1


    def test_activities_with_long_description_field(self, import_activities_long_field):
        """Activities should load even when a narrative exceeds the default CSV field
        size limit

        Some publishers put a whole project document in a description narrative, which
        is larger than the 131072 default of ``csv.field_size_limit``. Reading the CSV
        then raises ``_csv.Error``, which aborted the entire import run.
        See https://github.com/iati-data-access/data-backend/issues/38

        The fixture holds three consecutive activities taken from the publisher whose
        data caused that failure, the middle one carrying the long narratives. They are
        truncated to 135000 characters -- just over the limit -- to keep the fixture to
        a reasonable size.
        """
        activities = IATIActivity.query.all()
        assert len(activities) == 3

        activity = IATIActivity.query.filter_by(
            iati_identifier='XM-DAC-41317-SAP058').first()
        assert len(activity.description) == 135000

        # The activity following the oversized one must still be imported: it was
        # everything after the failure point that was lost in production.
        assert IATIActivity.query.filter_by(
            iati_identifier='XM-DAC-41317-FP082').first() is not None


    @pytest.fixture
    def low_csv_field_size_limit(self):
        """Lower the field size limit so a small fixture can breach it

        ``csv.field_size_limit`` is process-global, so it is restored afterwards. The
        good fixture's longest field is 1900 characters, well under this.
        """
        original_limit = csv.field_size_limit(5000)
        yield 5000
        csv.field_size_limit(original_limit)


    @pytest.fixture
    def import_activities_batch(self, low_csv_field_size_limit):
        yield import_data.import_activities_from_csvs(
            directory=os.path.join('tests', 'fixtures', 'activities', 'csv_batch'))
        db.session.execute(sa.delete(IATIActivity))


    def test_batch_continues_after_unreadable_file(self, import_activities_batch):
        """A file that cannot be read should be skipped, not abort the whole run

        In #38 a single unreadable activity file raised out of the import entirely, so
        ``import_budgets_transactions_from_csvs`` never ran and no financial data was
        updated for two months.

        The fixture directory holds an unreadable file (11111.csv, whose narratives
        exceed the limit) and a good one (44000.csv). The unreadable file sorts first,
        so the good file being imported is what proves the run carried on.
        """
        failed_files = import_activities_batch
        assert failed_files == ['11111.csv']

        # The good file, which sorts after the unreadable one, was still imported.
        assert IATIActivity.query.filter_by(
            iati_identifier='44000-P104716').first() is not None
        assert IATIActivity.query.filter_by(
            iati_identifier='44000-P105683').first() is not None

        # Nothing from the unreadable file was imported.
        assert IATIActivity.query.filter_by(
            iati_identifier='11111-UNREADABLE').first() is None
