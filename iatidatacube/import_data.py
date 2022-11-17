from normality import slugify
import re
import os
from iatidatacube.xlsx_to_csv import get_data
from iatidatacube.models import *
from iatidatacube.extensions import db
import iatikit
import iatiflattener
import pandas as pd
import time


def get_groups_or_none(possible_match, index):
    if possible_match is not None:
        return possible_match.groups()[index]
    return None


def add_row(row, known_reporting_organisations):
    il = IATILine()
    for key, value in row.items():
        _key = slugify(key).replace("-", "_")
        if _key in ('multi_country', 'humanitarian'):
            setattr(il, _key, {'0': False, '1': True, 0: False, 1: True}[value])
        elif _key in ('value_usd', 'value_eur', 'value_local_currrency'):
            setattr(il, _key, float(value))
        elif _key in ("reporting_organisation"):
            ro = get_groups_or_none(re.match(r"(.*) \[(.*)\]",
                value), 1)
            if ro not in known_reporting_organisations:
                print(f"Reporting organisation {ro} not recognised, skipping.")
                return
            il.reporting_organisation = ro
        elif _key in ("reporting_organisation_type",
            "provider_organisation_type",
            "receiver_organisation_type",
            "aid_type", "finance_type", "flow_type",
            "transaction_type", "sector_category", "sector",
            "recipient_country_or_region"):
            setattr(il, _key, get_groups_or_none(re.match(r"(\w*) - (.*)", value), 0))
        elif _key in ("title"):
            if IATIActivity.query.get(row['IATI Identifier']) is None:
                act = IATIActivity()
                act.iati_identifier = row['IATI Identifier']
                act.title = row['Title']
                db.session.add(act)
        else:
            setattr(il, _key, value)
    db.session.add(il)


def import_data(filename, known_reporting_organisations):
    print(f"Importing data for file {filename}")
    csv_reader = get_data(filename, None, "Data")
    for i, row in enumerate(csv_reader):
        try:
            add_row(row, known_reporting_organisations)
        except Exception as e:
            print(f"Couldn't add row {i}, exception was {e}")
            db.session.rollback()
        if i % 1000: db.session.commit()
    db.session.commit()


def import_all_files():
    known_reporting_organisations = [ro.code for ro in ReportingOrganisation.query.all()]
    files = sorted([file for file in os.listdir('../data-en/') if file.endswith(".xlsx") and not file.startswith('~')])
    for file in files:
        try:
            import_data(f"../data-en/{file}", known_reporting_organisations)
        except Exception as e:
            print(f"Exception with file {file}", e)


def import_country(country_code='AF'):
    start = time.time()
    known_reporting_organisations = [ro.code for ro in ReportingOrganisation.query.all()]
    import_data(f"../data-en/{country_code}.xlsx", known_reporting_organisations)
    end = time.time()
    print(f"Processed {csv_file} in {end-start}s")


def setup_db():
    db.create_all()


def drop_db():
    db.drop_all()


def add_row_from_csv(row, known_reporting_organisations, known_iati_identifiers):
    il = IATILine()
    for key, value in row.items():
        map_keys = {
            'reporting_org_type': 'reporting_organisation_type',
            'provider_org#en': 'provider_organisation',
            'provider_org_type': 'provider_organisation_type',
            'receiver_org#en': 'receiver_organisation',
            'receiver_org_type': 'receiver_organisation_type',
            'country_code': 'recipient_country_or_region',
            'sector_code': 'sector',
            'fiscal_year': 'calendar_year',
            'fiscal_quarter': 'calendar_quarter',
            'fiscal_year_quarter': 'calendar_year_and_quarter',
            'value_local': 'value_local_currrency'
        }
        _key = map_keys.get(key, key)
        if _key in ('multi_country', 'humanitarian'):
            setattr(il, _key, {'0': False, '1': True, 0: False, 1: True}[value])
        elif _key in ('value_usd', 'value_eur', 'value_local_currrency'):
            setattr(il, _key, float(value))
        elif _key in ("reporting_org#en"):
            ro = get_groups_or_none(re.match(r"(.*) \[(.*)\]",
                value), 1)
            if ro not in known_reporting_organisations:
                print(f"Reporting organisation {ro} not recognised, skipping.")
                return
            il.reporting_organisation = ro
        elif _key in ("reporting_organisation_type",
            "provider_organisation",
            "provider_organisation_type",
            "receiver_organisation",
            "receiver_organisation_type",
            "aid_type", "finance_type", "flow_type",
            "transaction_type", "sector_category", "sector",
            "recipient_country_or_region", "calendar_year",
            "calendar_quarter", "calendar_year_and_quarter"):
            setattr(il, _key, value)
        elif _key in ("title#en"):
            if row['iati_identifier'] not in known_iati_identifiers:
                act = IATIActivity()
                act.iati_identifier = row['iati_identifier']
                act.title = row['title#en']
                db.session.add(act)
                known_iati_identifiers.append(row['iati_identifier'])
        else:
            setattr(il, _key, value)
    db.session.add(il)
    return known_iati_identifiers


def import_from_csv(csv_file, known_reporting_organisations):
    print(f"Loading {csv_file}")
    langs = ['en']
    CSV_HEADERS = iatiflattener.lib.variables.headers(langs)
    _DTYPES = iatiflattener.lib.variables.dtypes(langs)
    headers = iatiflattener.lib.variables.group_by_headers_with_langs(langs)
    CSV_HEADER_DTYPES = dict(map(lambda csv_header: (csv_header[1], _DTYPES[csv_header[0]]), enumerate(CSV_HEADERS)))
    df = pd.read_csv(os.path.join('output', 'csv', csv_file), dtype=CSV_HEADER_DTYPES)
    df = df.groupby(headers)
    df = df.agg({'value_usd':'sum','value_eur':'sum','value_local':'sum'})
    df = df.reset_index()
    #df = df.fillna(no_data)
    #print(df.head())
    known_iati_identifiers = [row.iati_identifier for row in IATIActivity.query.with_entities(IATIActivity.iati_identifier).all()]
    for i, row in df.iterrows():
        try:
            known_iati_identifiers = add_row_from_csv(row, known_reporting_organisations, known_iati_identifiers)
        except Exception as e:
            print(f"Couldn't add row {i}, exception was {e}")
            db.session.rollback()
        if i % 2000: db.session.commit()
    db.session.commit()


def fetch_data():
    iatikit.download.data()


def process_data():
    langs = ['en']
    os.makedirs('output/csv/', exist_ok=True)
    iatiflattener.FlattenIATIData(refresh_rates=True,
        langs=langs)


def import_all():
    langs = ['en']
    known_reporting_organisations = [ro.code for ro in ReportingOrganisation.query.all()]
    files_to_import = sorted(os.listdir('output/csv/'))
    for csv_file in files_to_import:
        if not csv_file.endswith('.csv'): continue
        start = time.time()
        import_from_csv(csv_file, known_reporting_organisations)
        end = time.time()
        print(f"Processed {csv_file} in {end-start}s")