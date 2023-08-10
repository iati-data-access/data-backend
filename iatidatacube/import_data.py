from normality import slugify
import re
import os
import shutil
from iatidatacube.xlsx_to_csv import get_data
from iatidatacube.models import *
from iatidatacube.extensions import db
import iatikit
import iatiflattener
from iatiflattener import group_data
import pandas as pd
import csv
import datetime
import hashlib
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as postgres_insert


from functools import wraps
import time


def timeit(f_py=None, arguments_to_output=[]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = end_time - start_time
            _args = "; ".join([f'{arg[0]}={arg[1]}' for arg in dict(**kwargs).items() if arg[0] in arguments_to_output])
            if len(_args) > 0:
                _args = ' with arguments ' + _args
            print(f'Function {func.__name__}{_args} Took {total_time:.4f} seconds')
            return result
        return wrapper
    return decorator(f_py) if callable(f_py) else decorator


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


@timeit(arguments_to_output=['csv_file'])
def delete_dataset(csv_file, inserted_ids):
    print(f"Deleting ids no longer existing for {csv_file}")
    dataset_type, dataset_country = re.match("(.*)-(.*).csv", csv_file).groups()
    if dataset_type == 'budget':
        q = sa.sql.expression.select(IATILine.id).where(
            IATILine.recipient_country_or_region==dataset_country,
            IATILine.transaction_type=='budget'
        ).order_by(IATILine.id)
        identifiers_budgets = [row.id for row in db.session.execute(q)]
        identifiers_to_delete = list(filter(lambda identifier: identifier not in inserted_ids, identifiers_budgets))
    else:
        q = sa.sql.expression.select(IATILine.id).where(
            IATILine.recipient_country_or_region==dataset_country,
            IATILine.transaction_type!='budget'
        ).order_by(IATILine.id)
        identifiers_transactions = set([row.id for row in db.session.execute(q)])
        identifiers_to_delete = list(filter(lambda identifier: identifier not in inserted_ids, identifiers_transactions))
    print("There are identifiers to delete", identifiers_to_delete)
    if len(identifiers_to_delete) == 0: return
    statement = sa.delete(IATILine).where(
        IATILine.id.in_(identifiers_to_delete))
    db.session.execute(statement)
    db.session.commit()


def row_from_csv(row, codelists, reporting_organisation,
    provider_organisations, receiver_organisations,
    langs = ['en', 'fr', 'es', 'pt']):
    il = {}
    for key, value in row.items():
        map_keys = {
            'reporting_org_group': 'reporting_organisation_group',
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
            il[_key] = {'0': False, '1': True, 0: False, 1: True}[value]
        elif _key in ('value_usd', 'value_eur', 'value_local_currrency'):
            il[_key] = float(value)
        elif _key in ("aid_type", "finance_type", "flow_type",
            "transaction_type", "sector_category", "sector",
            "reporting_organisation_type",
            "provider_organisation_type",
            "receiver_organisation_type"):
            if value not in codelists[_key]:
                value = None
            il[_key] = value
        elif _key in (
            "provider_organisation",
            "provider_organisation_fr",
            "provider_organisation_es",
            "provider_organisation_pt",
            "receiver_organisation",
            "receiver_organisation_fr",
            "receiver_organisation_es",
            "receiver_organisation_pt",
            "aid_type", "finance_type", "flow_type",
            "transaction_type", "sector_category", "sector",
            "recipient_country_or_region", "calendar_year",
            "calendar_quarter", "calendar_year_and_quarter",
            "iati_identifier", "reporting_organisation_group",
            "url"):
            il[_key] = value
        # The following column names are ignored:
        # title#fr, title#en, title#es, title#pt => on activities
        # reporting_org#en, reporting_org#es, reporting_org#fr, reporting_org#pt => we just use the reference
    _hash = hashlib.sha256()
    _hash.update("".join([str(val) for val in il.values()]).encode())
    il['id'] = _hash.hexdigest()
    il['reporting_organisation'] = reporting_organisation
    il['provider_organisation_id'] = make_organisations_hash(dict([(f'provider_org#{lang}', row[f'provider_org#{lang}']) for lang in langs]))
    il['receiver_organisation_id'] = make_organisations_hash(dict([(f'provider_org#{lang}', row[f'receiver_org#{lang}']) for lang in langs]))
    return il


@timeit
def import_all_activities(start_at='', end_at='', force_update=False):
    files_to_import = sorted(os.listdir('output/csv/activities/'))
    if start_at != '':
        start = False
    else: start = True
    for csv_file in files_to_import:
        if not csv_file.endswith('.csv'): continue
        if (csv_file != start_at) and (start == False):
            continue
        start = time.time()
        import_activities(csv_file=csv_file, force_update=force_update)
        end = time.time()
        print(f"Processed {csv_file} in {end-start}s")
        if (csv_file == end_at): break


@timeit(arguments_to_output=['csv_file'])
def import_activities(csv_file, force_update=False, directory=os.path.join('output', 'csv', 'activities')):
    reporting_organisation_ref = None
    iati_identifiers = []
    csv_file_path = os.path.join(directory, csv_file)
    with open(csv_file_path, 'r') as _csv_file:
        csvreader = csv.DictReader(_csv_file)
        activities = []
        reporting_organisation_ref = csv_file.split('.csv')[0]
        existing_activities_hashes = dict([(activity.iati_identifier, activity._hash) for activity in \
            IATIActivity.query.filter_by(
                    reporting_organisation=reporting_organisation_ref).all()])
        for activity_row in csvreader:
            iati_identifier = activity_row['iati_identifier']
            if iati_identifier in iati_identifiers:
                continue
            iati_identifiers.append(iati_identifier)
            if (activity_row['hash'] == existing_activities_hashes.get(activity_row['iati_identifier'])
                ) and (force_update is False):
                continue
            iati_identifiers.append(iati_identifier)
            activities.append(add_or_update_activity(activity_row))

        print(f"Inserting / updating {len(activities)} activities")
        if len(activities) == 0: return
        stmt = postgres_insert(IATIActivity).values(activities)
        stmt = stmt.on_conflict_do_update(
            index_elements=['iati_identifier'],
            set_={col: getattr(stmt.excluded, col) for col in IATIActivity.__table__.columns.keys()})
        db.session.execute(stmt)
        db.session.commit()

    # Handle deleted IATI identifiers
    identifiers_to_delete = filter(lambda identifier: identifier not in iati_identifiers, existing_activities_hashes.keys())

    statement = sa.delete(IATIActivity).where(
        IATIActivity.iati_identifier.in_(identifiers_to_delete))
    db.session.execute(statement)
    db.session.commit()


def iso_date(value):
    return datetime.datetime.strptime(value, '%Y-%m-%d').date()


def add_or_update_activity(activity_row):
    activity = {}
    activity['iati_identifier'] = activity_row['iati_identifier']
    activity['title'] = activity_row['title#en']
    activity['title_fr'] = activity_row['title#fr']
    activity['title_es'] = activity_row['title#es']
    activity['title_pt'] = activity_row['title#pt']
    activity['description'] = activity_row['description#en']
    activity['description_fr'] = activity_row['description#fr']
    activity['description_es'] = activity_row['description#es']
    activity['description_pt'] = activity_row['description#pt']
    activity['glide'] = activity_row['GLIDE']
    activity['hrp'] = activity_row['HRP']
    activity['location'] = activity_row['location']
    activity['_hash'] = activity_row['hash']
    activity['reporting_organisation'] = activity_row['reporting_org_ref']
    try:
        activity['start_date'] = iso_date(activity_row['start_date'])
    except ValueError:
        activity['start_date'] = None
    try:
        activity['end_date'] = iso_date(activity_row['end_date'])
    except ValueError:
        activity['end_date'] = None
    return activity


def get_reporting_org(reporting_orgs, row):
    ro_row = row['reporting_org#en']
    if ro_row not in reporting_orgs:
        ro_row_ref = get_groups_or_none(re.match(r"(.*) \[(.*)\]",
                ro_row), 1)
        reporting_orgs[ro_row] = ro_row_ref
    return reporting_orgs, reporting_orgs.get(ro_row)


def make_organisations_hash(data):
    _hash = hashlib.sha256()
    _hash.update("".join(data.values()).encode())
    return _hash.hexdigest()


@timeit(arguments_to_output=['provider_receiver'])
def get_organisations(df, provider_receiver='provider', langs=['en', 'fr', 'es', 'pt']):
    records = df[
        [f'{provider_receiver}_org#{lang}' for lang in langs]
        ].drop_duplicates().to_dict(orient='records')
    _records = {}
    for record in records:
        _record = {}
        _record['id'] = make_organisations_hash(record)
        # Don't create duplicate organisations
        if _record['id'] in _records: continue
        for lang in langs:
            _record[f'name_{lang}'] = record[f'{provider_receiver}_org#{lang}']
        _records[_record['id']] = _record
    if len(_records) == 0: return {}

    table = {'provider': ProviderOrganisation, 'receiver': ReceiverOrganisation}[provider_receiver]
    stmt = postgres_insert(table).values(list(_records.values()))
    stmt = stmt.on_conflict_do_update(
        constraint=f'{provider_receiver}_organisation_pkey',
        set_={col: getattr(stmt.excluded, col) for col in table.__table__.columns.keys()})
    db.session.execute(stmt)
    db.session.commit()
    return _records


@timeit(arguments_to_output=['csv_file'])
def get_dataframe(csv_file, langs, directory):
    print(f"Loading {csv_file}")
    CSV_HEADERS = iatiflattener.lib.variables.headers(langs)
    _DTYPES = iatiflattener.lib.variables.dtypes(langs)
    headers = iatiflattener.lib.variables.group_by_headers_with_langs(langs)
    CSV_HEADER_DTYPES = dict(map(lambda csv_header: (csv_header[1], _DTYPES[csv_header[0]]), enumerate(CSV_HEADERS)))
    # Don't read 'NA' as a NA value (it is Namibia)
    df = pd.read_csv(os.path.join(directory, csv_file), dtype=CSV_HEADER_DTYPES)
    if 'NA' in csv_file:
        df.country_code = df.country_code.fillna('NA')
    all_relevant_headers = headers + ['value_usd', 'value_eur', 'value_local']
    df = df[all_relevant_headers]
    df = df.fillna('')
    df = df.groupby(headers)
    df = df.agg({'value_usd':'sum','value_eur':'sum','value_local':'sum'})
    df = df.reset_index()
    return df


@timeit(arguments_to_output=[])
def insert_or_update_rows(df, codelists, provider_organisations, receiver_organisations):
    print("Inserting / updating financial data")
    reporting_orgs = {}
    rows_to_insert = []
    inserted_ids = []

    def do_insert(rows_to_insert):
        if len(rows_to_insert) == 0: return []
        stmt = postgres_insert(IATILine).values(rows_to_insert)
        stmt = stmt.on_conflict_do_nothing(
          index_elements=['id'])
        db.session.execute(stmt)
        db.session.commit()
        return [row['id'] for row in rows_to_insert]

    for i, row in df.iterrows():
        reporting_orgs, reporting_org = get_reporting_org(reporting_orgs, row)
        if reporting_org not in codelists['reporting_organisation']:
            print(f"Reporting organisation {reporting_org} not recognised, skipping.")
            continue
        try:
            data = row_from_csv(row, codelists, reporting_org, provider_organisations, receiver_organisations)
            rows_to_insert.append(data)
        except Exception as e:
            print(f"Couldn't get data for row {i}, exception was {e}")
            db.session.rollback()
        # Insert / update for every 100,000 rows
        if i % 100000 == 0:
            inserted_ids += do_insert(rows_to_insert)
            rows_to_insert = []
    inserted_ids += do_insert(rows_to_insert)
    return inserted_ids


@timeit(arguments_to_output=['csv_file'])
def import_from_csv(csv_file, codelists,
        langs=['en', 'fr', 'es', 'pt'],
        directory=os.path.join('output', 'csv')):
    add_or_update_dataset(csv_file=csv_file, status='processing')
    df = get_dataframe(csv_file=csv_file, langs=langs, directory=directory)
    print(f"Creating provider organisations")
    provider_organisations = get_organisations(df=df,
        provider_receiver='provider', langs=langs)
    receiver_organisations = get_organisations(df=df,
        provider_receiver='receiver', langs=langs)
    inserted_ids = insert_or_update_rows(df=df, codelists=codelists,
        provider_organisations=provider_organisations,
        receiver_organisations=receiver_organisations)
    delete_dataset(csv_file=csv_file, inserted_ids=inserted_ids)
    add_or_update_dataset(csv_file=csv_file, status='complete')


def fetch_data():
    iatikit.download.data()


def process_data(langs=['en', 'fr', 'es', 'pt']):
    os.makedirs('output/csv/', exist_ok=True)
    iatiflattener.FlattenIATIData(refresh_rates=True,
        langs=langs)


def group_all(start_at='', end_at='', langs=['en', 'fr', 'es', 'pt']):
    group_data.GroupFlatIATIData(langs=langs)
    os.makedirs('output/web/', exist_ok=True)
    shutil.rmtree('output/web/')
    os.makedirs('output/web/xlsx/', exist_ok=True)
    os.makedirs('output/web/csv/', exist_ok=True)
    shutil.copytree('output/xlsx/', 'output/web/xlsx/', dirs_exist_ok=True)
    shutil.copytree('output/csv/', 'output/web/csv/', dirs_exist_ok=True)


@timeit
def import_activities_files(force_update=False):
    print("Loading and updating all activities...")
    activity_files_to_import = sorted(os.listdir('output/csv/activities/'))
    for activity_csv_file in activity_files_to_import:
        if not activity_csv_file.endswith('.csv'): continue
        import_activities(csv_file=activity_csv_file,
            force_update=force_update)


@timeit
def import_all(start_at='', end_at='', langs=['en', 'fr', 'es', 'pt'], force_update=False):
    codelists = {
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
    import_activities_files(force_update)

    files_to_import = sorted(os.listdir('output/csv/'))
    if start_at != '':
        start = False
    else: start = True
    for csv_file in files_to_import:
        if not csv_file.endswith('.csv'): continue
        if (csv_file != start_at) and (start == False):
            continue
        import_from_csv(csv_file=csv_file, codelists=codelists)
        if (csv_file == end_at): break
