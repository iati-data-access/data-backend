from normality import slugify
import re
import os
from iatidatacube.xlsx_to_csv import get_data
from iatidatacube.models import *
from iatidatacube.extensions import db
import iatikit
import iatiflattener
from iatiflattener import group_data
import pandas as pd
import time
import csv
import datetime


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
        if i % 1000 == 0:
            db.session.commit()
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


def add_or_update_dataset(csv_file, status='processing'):
    dataset_type, dataset_country = re.match("(.*)-(.*).csv", csv_file).groups()
    dataset_id = f"{dataset_type}-{dataset_country}"
    dataset = Dataset.query.filter_by(
        id=dataset_id).first()
    if dataset is None:
        dataset = Dataset()
        dataset.id = dataset_id
        dataset.dataset_type = dataset_type
        dataset.country = dataset_country
        dataset.created_at = datetime.datetime.utcnow()
    if status == 'processing':
        dataset.processing_at = datetime.datetime.now()
        dataset.status = 1
    elif status == 'complete':
        dataset.updated_at = datetime.datetime.now()
        dataset.status = 2
    db.session.add(dataset)
    db.session.commit()


def delete_dataset(csv_file):
    dataset_type, dataset_country = re.match("(.*)-(.*).csv", csv_file).groups()
    if dataset_type == 'budget':
        statement = sa.delete(IATILine).where(
            IATILine.recipient_country_or_region==dataset_country
        ).where(
            IATILine.transaction_type=='budget'
        )
        db.session.execute(statement)
    else:
        statement = sa.delete(IATILine).where(
            IATILine.recipient_country_or_region==dataset_country
        ).where(
            IATILine.transaction_type!='budget'
        )
        db.session.execute(statement)


def add_row_from_csv(row, codelists, reporting_organisation):
    il = IATILine()
    for key, value in row.items():
        map_keys = {
            'reporting_org_type': 'reporting_organisation_type',
            'provider_org#en': 'provider_organisation',
            'provider_org#fr': 'provider_organisation_fr',
            'provider_org#es': 'provider_organisation_es',
            'provider_org#pt': 'provider_organisation_pt',
            'provider_org_type': 'provider_organisation_type',
            'receiver_org#en': 'receiver_organisation',
            'receiver_org#fr': 'receiver_organisation_fr',
            'receiver_org#es': 'receiver_organisation_es',
            'receiver_org#pt': 'receiver_organisation_pt',
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
            il.reporting_organisation = reporting_organisation
        elif _key in ("aid_type", "finance_type", "flow_type",
            "transaction_type", "sector_category", "sector"):
            if value not in codelists[_key]:
                value = None
            setattr(il, _key, value)
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
        else:
            setattr(il, _key, value)
    db.session.add(il)


def import_all_activities(start_at='', end_at=''):
    files_to_import = sorted(os.listdir('output/csv/activities/'))
    if start_at != '':
        start = False
    else: start = True
    for csv_file in files_to_import:
        if not csv_file.endswith('.csv'): continue
        if (csv_file != start_at) and (start == False):
            continue
        start = time.time()
        import_activities(csv_file)
        end = time.time()
        print(f"Processed {csv_file} in {end-start}s")
        if (csv_file == end_at): break


def import_activities(csv_file):
    reporting_organisation_ref = None
    iati_identifiers = []
    csv_file_path = os.path.join('output', 'csv', 'activities', csv_file)
    with open(csv_file_path, 'r') as _csv_file:
        csvreader = csv.DictReader(_csv_file)
        for activity_row in csvreader:
            reporting_organisation_ref = activity_row['reporting_org_ref']
            iati_identifiers.append(activity_row['iati_identifier'])
            add_or_update_activity(activity_row)
        db.session.commit()
    # Handle deleted IATI identifiers


def iso_date(value):
    return datetime.datetime.strptime(value, '%Y-%m-%d').date()


def add_or_update_activity(activity_row):
    activity = IATIActivity.query.filter(
        IATIActivity.iati_identifier==activity_row['iati_identifier']).first()
    if activity is None:
        activity = IATIActivity()
        activity.iati_identifier = activity_row['iati_identifier']
    activity.title = activity_row['title#en']
    activity.title_fr = activity_row['title#fr']
    activity.title_es = activity_row['title#es']
    activity.title_pt = activity_row['title#pt']
    activity.description = activity_row['description#en']
    activity.description_fr = activity_row['description#fr']
    activity.description_es = activity_row['description#es']
    activity.description_pt = activity_row['description#pt']
    activity.glide = activity_row['GLIDE']
    activity.hrp = activity_row['HRP']
    activity.location = activity_row['location']
    try:
        activity.start_date = iso_date(activity_row['start_date'])
        activity.end_date = iso_date(activity_row['end_date'])
    except ValueError:
        pass
    db.session.add(activity)


def get_reporting_org(reporting_orgs, row):
    ro_row = row['reporting_org#en']
    if ro_row not in reporting_orgs:
        ro_row_ref = get_groups_or_none(re.match(r"(.*) \[(.*)\]",
                ro_row), 1)
        reporting_orgs[ro_row] = ro_row_ref
    return reporting_orgs, reporting_orgs.get(ro_row)


def import_from_csv(csv_file, codelists, langs=['en', 'fr', 'es', 'pt']):
    add_or_update_dataset(csv_file, 'processing')
    print(f"Deleting existing dataset for {csv_file}")
    delete_dataset(csv_file)
    print(f"Loading {csv_file}")

    start = time.time()
    CSV_HEADERS = iatiflattener.lib.variables.headers(langs)
    _DTYPES = iatiflattener.lib.variables.dtypes(langs)
    headers = iatiflattener.lib.variables.group_by_headers_with_langs(langs)
    CSV_HEADER_DTYPES = dict(map(lambda csv_header: (csv_header[1], _DTYPES[csv_header[0]]), enumerate(CSV_HEADERS)))
    # Don't read 'NA' as a NA value (it is Namibia)
    df = pd.read_csv(os.path.join('output', 'csv', csv_file), dtype=CSV_HEADER_DTYPES)
    if 'NA' in csv_file:
        df.country_code = df.country_code.fillna('NA')
    all_relevant_headers = headers + ['value_usd', 'value_eur', 'value_local']
    df = df[all_relevant_headers]
    df = df.fillna('')
    df = df.groupby(headers)
    df = df.agg({'value_usd':'sum','value_eur':'sum','value_local':'sum'})
    df = df.reset_index()
    end = time.time()
    print(f"Reading data took {end-start}s")

    start = time.time()
    reporting_orgs = {}
    for i, row in df.iterrows():
        reporting_orgs, reporting_org = get_reporting_org(reporting_orgs, row)
        if reporting_org not in codelists['reporting_organisation']:
            print(f"Reporting organisation {reporting_org} not recognised, skipping.")
            continue
        try:
            add_row_from_csv(row, codelists, reporting_org)
        except Exception as e:
            print(f"Couldn't add row {i}, exception was {e}")
            db.session.rollback()
        if i % 1000 == 0:
            db.session.commit()
    db.session.commit()
    end = time.time()
    print(f"Committing rows took {end-start}s")
    add_or_update_dataset(csv_file, 'complete')


def fetch_data():
    iatikit.download.data()


def process_data(langs=['en', 'fr', 'es', 'pt']):
    os.makedirs('output/csv/', exist_ok=True)
    iatiflattener.FlattenIATIData(refresh_rates=True,
        langs=langs)


def group_all(start_at='', end_at='', langs=['en', 'fr', 'es', 'pt']):
    group_data.GroupFlatIATIData(langs=langs)


def import_all(start_at='', end_at='', langs=['en', 'fr', 'es', 'pt']):
    codelists = {
        "reporting_organisation": [item.code for item in ReportingOrganisation.query.all()],
        "aid_type": [item.code for item in AidType.query.all()],
        "finance_type": [item.code for item in FinanceType.query.all()],
        "flow_type": [item.code for item in FlowType.query.all()],
        "transaction_type": [item.code for item in TransactionType.query.all()],
        "sector_category": [item.code for item in SectorCategory.query.all()],
        "sector": [item.code for item in Sector.query.all()],
        "recipient_country_or_region": [item.code for item in RecipientCountryorRegion.query.all()]
    }
    print("Loading and updating all activities...")
    start = time.time()
    activity_files_to_import = sorted(os.listdir('output/csv/activities/'))
    for activity_csv_file in activity_files_to_import:
        if not activity_csv_file.endswith('.csv'): continue
        import_activities(activity_csv_file)
    end = time.time()
    print(f"Loaded all activities in {end-start}s")

    files_to_import = sorted(os.listdir('output/csv/'))
    if start_at != '':
        start = False
    else: start = True
    for csv_file in files_to_import:
        if not csv_file.endswith('.csv'): continue
        if (csv_file != start_at) and (start == False):
            continue
        start = time.time()
        import_from_csv(csv_file, codelists)
        end = time.time()
        print(f"Processed {csv_file} in {end-start}s")
        if (csv_file == end_at): break
