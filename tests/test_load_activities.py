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
        yield import_data.import_activities(csv_file='44000.csv',
            force_update=False,
            directory=os.path.join('tests', 'fixtures', 'activities', 'csv'))
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
        import_data.import_activities(csv_file='44000.csv',
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
        import_data.import_activities(csv_file='44000.csv',
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
        import_data.import_activities(csv_file='44000.csv',
            force_update=True,
            directory=os.path.join('tests', 'fixtures', 'activities', 'csv_delete'))
        activity = IATIActivity.query.filter_by(
            iati_identifier='44000-P104716').first()
        assert activity is None
        activities = IATIActivity.query.all()
        assert len(activities) == 1
