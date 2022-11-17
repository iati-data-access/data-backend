import requests
from iatidatacube.models import *
from iatidatacube.extensions import db

codelists_url = "https://codelists.codeforiati.org/api/json/{}/{}.json"


def get_multilang_codelist(codelist_name,
        aggregate_by='code', aggregate_name='name'):
    req = requests.get(codelists_url.format('en', codelist_name))
    codelist = dict([(item[aggregate_by], {
        'name_en': item.get(aggregate_name),
        'type': item.get('codeforiati:organisation-type-code')
    }) for item in req.json()['data']])
    for lang in ['fr', 'es', 'pt']:
        req = requests.get(codelists_url.format(lang, codelist_name))
        req_data = dict([(item[aggregate_by], item.get(aggregate_name)) for item in req.json()['data']])
        for code, data in codelist.items():
            codelist[code][f'name_{lang}'] = req_data.get(code) or data['name_en']
    return codelist

def write_codelist_values(codelist_name, codelist):
    for code, names in codelist.items():
        cl = eval(f"{codelist_name}()")
        cl.code = code
        for name_key, name_value in names.items():
            setattr(cl, name_key, name_value)
        db.session.add(cl)


def import_codelist(codelist_name):
    codelist = get_multilang_codelist(codelist_name)
    write_codelist_values(codelist_name, codelist)
    db.session.commit()


def import_codelists():
    print("Importing codelists")
    codelist_columns = ['ReportingOrganisation', 'AidType',
        'FinanceType', 'FlowType', 'TransactionType', 'Sector',
        'OrganisationType']
    for codelist_column in codelist_columns:
        import_codelist(codelist_column)
    countries = get_multilang_codelist("Country")
    regions = get_multilang_codelist("Region")
    write_codelist_values("RecipientCountryorRegion", countries)
    write_codelist_values("RecipientCountryorRegion", regions)
    budget_tt = {'budget': {
        'name_en': 'Budget',
        'name_fr': 'Budget',
        'name_es': 'Budget',
        'name_pt': 'Budget'
    }}
    write_codelist_values("TransactionType", budget_tt)

    sectorgroup = get_multilang_codelist("SectorGroup",
        aggregate_by='codeforiati:group-code',
        aggregate_name='codeforiati:group-name')
    write_codelist_values('SectorCategory', sectorgroup)

    db.session.commit()
