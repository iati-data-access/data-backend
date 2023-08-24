import requests
from collections import namedtuple
from iatidatacube.models import *
from iatidatacube.extensions import db
import iatiflattener
from iatidatacube.import_data import timeit

codelists_url = "https://codelists.codeforiati.org/api/json/{}/{}.json"

CodelistMetadata = namedtuple("CodelistMetadata",
                              ["codelist_name", "target_columns", "with_no_data", "aggregate_by", "aggregate_name"])


def get_codelist_from_request(lang, codelist_name):
    response = requests.get(codelists_url.format(lang, codelist_name))
    return response.json()


def get_multilang_codelist(codelist_name, aggregate_by='code', aggregate_name='name'):
    """Fetches a codelist with entries for the specified languages."""

    req = get_codelist_from_request('en', codelist_name)

    codelist = dict([(item[aggregate_by], {
        'name_en': item.get(aggregate_name),
        'type': item.get('codeforiati:organisation-type-code')
    }) for item in req['data']])

    for lang in ['fr', 'es', 'pt']:
        req = get_codelist_from_request(lang, codelist_name)
        req_data = dict([(item[aggregate_by], item.get(aggregate_name)) for item in req['data']])
        # populate the list for other languages, using the English value as a default
        for code, data in codelist.items():
            codelist[code][f'name_{lang}'] = req_data.get(code) or data['name_en']

    return codelist


def add_codelist_values_to_db(codelist_name, codelist, with_no_data=True):
    """Adds the values from a codelist to the DB"""

    translations = iatiflattener.lib.variables.TRANSLATIONS
    if with_no_data is True:
        codelist[''] = {
            'name_en': translations.get('en').get('no-data'),
            'name_fr': translations.get('fr').get('no-data'),
            'name_es': translations.get('es').get('no-data'),
            'name_pt': translations.get('pt').get('no-data')
        }
    for code, names in codelist.items():
        # Check if this code already exists
        cl = eval(f"{codelist_name}").query.filter_by(code=code).first()
        if cl is None:
            cl = eval(f"{codelist_name}()")

        cl.code = code
        for name_key, name_value in names.items():
            setattr(cl, name_key, name_value)
        db.session.add(cl)


def import_codelist(codelist_metadata: CodelistMetadata):
    codelist = get_multilang_codelist(codelist_metadata.codelist_name,
                                      aggregate_by=codelist_metadata.aggregate_by,
                                      aggregate_name=codelist_metadata.aggregate_name)

    for target_column in codelist_metadata.target_columns:
        add_codelist_values_to_db(target_column, codelist, codelist_metadata.with_no_data)

    db.session.commit()


@timeit
def import_codelists():
    """Writes various codelists to the database, with some minimal processing in certain cases"""

    print("Importing codelists")

    codelists_metadata = [CodelistMetadata('ReportingOrganisation', ['ReportingOrganisation'], True, "code", "name"),
                          CodelistMetadata('AidType', ['AidType'], True, "code", "name"),
                          CodelistMetadata('FinanceType', ['FinanceType'], True, "code", "name"),
                          CodelistMetadata('FlowType', ['FlowType'], True, "code", "name"),
                          CodelistMetadata('TransactionType', ['TransactionType'], True, "code", "name"),
                          CodelistMetadata('Sector', ['Sector'], True, "code", "name"),
                          CodelistMetadata('OrganisationType',
                                           ['OrganisationType', 'ProviderOrganisationType', 'ReceiverOrganisationType'],
                                           True, "code", "name"),
                          CodelistMetadata('Country', ['RecipientCountryorRegion'], True, "code", "name"),
                          CodelistMetadata('Region', ['RecipientCountryorRegion'], False, "code", "name"),
                          CodelistMetadata('SectorGroup', ['SectorCategory'], True,
                                           "codeforiati:group-code", "codeforiati:group-name"),
                          CodelistMetadata('ReportingOrganisationGroup', ['ReportingOrganisationGroup'], True,
                                           "codeforiati:group-code", "codeforiati:group-name")
                          ]

    for codelist_metadata in codelists_metadata:
        import_codelist(codelist_metadata)

    # add this special case manually
    budget_tt = {'budget': {
        'name_en': 'Budget',
        'name_fr': 'Budget',
        'name_es': 'Budget',
        'name_pt': 'Budget'
    }}
    add_codelist_values_to_db("TransactionType", budget_tt, False)

    db.session.commit()
