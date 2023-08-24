import os, json

import pytest
import sqlalchemy as sa

from iatidatacube import import_codelists
from iatidatacube.models import *


@pytest.mark.usefixtures('client_class')
class TestCodelists:
    @pytest.fixture
    def codelists_data(self):
        yield import_codelists.import_codelists()
        for table in [ReportingOrganisation, AidType,
                      FinanceType, FlowType, TransactionType, Sector,
                      OrganisationType, RecipientCountryorRegion,
                      SectorCategory, ReportingOrganisationGroup]:
            db.session.execute(sa.delete(table))

    def test_reporting_orgs_loaded(self, codelists_data):
        reporting_orgs = ReportingOrganisation.query.all()
        assert len(reporting_orgs) == 1623

    def test_update_reporting_org(self, monkeypatch, codelists_data):
        reporting_org = ReportingOrganisation.query.filter_by(code='AU-5').first()
        assert reporting_org.name_en == 'Australia - Department of Foreign Affairs and Trade'

        def mock_get_altered_codelist(lang, codelist_name):
            with open(os.path.join('tests', 'fixtures', "codelists", lang, f'{codelist_name}.json')) as codelist_file:
                codelist_data = json.load(codelist_file)
            if lang == 'en':
                assert codelist_data['data'][0]['code'] == 'AU-5'
                codelist_data['data'][0]['name'] = 'TEST'
            return codelist_data

        monkeypatch.setattr(import_codelists, "get_codelist_from_request", mock_get_altered_codelist)
        import_codelists.import_codelist(
            import_codelists.CodelistMetadata('ReportingOrganisation', ['ReportingOrganisation'],
                                              True, "code", "name"))

        reporting_org = ReportingOrganisation.query.filter_by(code='AU-5').first()
        assert reporting_org.name_en == 'TEST'
