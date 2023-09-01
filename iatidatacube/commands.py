"""Click commands."""
import click
from flask.cli import with_appcontext
from iatidatacube.import_data import (create_database, drop_db, fetch_data, group_all, import_activities_from_csvs,
                                      import_budgets_transactions_from_csvs, process_data)
from iatidatacube.import_codelists import import_codelists


@click.command()
@with_appcontext
def setup_codelists():
    """Downloads the codelists, processes them if needed, and writes them to the DB."""

    import_codelists()


@click.command()
@with_appcontext
def create_db():
    """This creates the database.

    This dedicated command is needed because ``flask db upgrade`` doesn't work after a ``flask drop-all`` command.
    """

    create_database()


@click.command()
@with_appcontext
def drop_all():
    """Drops all tables from the database."""

    if click.confirm("Are you sure you would like to drop all data in the database? This action cannot be undone!"):
        print("Dropping DB.")
        drop_db()
    else:
        print("Aborting.")


@click.command()
@with_appcontext
def download():
    """Downloads all data from the Code for IATI data dump (using iatikit downloader).

    Unpacks the data dump ZIP into __iatikitcache__ directory."""

    fetch_data()


@click.command()
@with_appcontext
def process():
    """Uses ``iati_flattener`` library to flatten (group) the XML data into a set of CSV files.

    IATI Flattener takes the source data (IATI XML files) and groups the data into sets of CSV files. It groups the
    data in three ways:
    - activities (``//iati-activity``) are grouped into files by publisher; each row is an iati activity.
    - budgets (IATI Activity XML Path: ``//iati-activity[budget]``) are grouped into files by region or country
      (stored as ``budget-CODE.csv``, where CODE is a region or country code); budgets are split over sectors,
      quarters, aid types, and/or flow types, so there may be multiple budget rows in a single file for the
      same IATI budget.
      The original value will be prorated out; the sum of the various rows will add up to the original value
      of the budget. Because budgets may be applicable to multiple countries or regions, the same budget may
      appear in multiple region/country files.
    - transactions (IATI Activity XML Path: //transaction) are grouped by region or country (stored as
      ``transaction-CODE.csv``, where CODE is a region or country code); transactions are split over sectors and
      quarters, so there may be multiple transaction rows for a given IATI transaction (they can also be split
      over regions/countries). The original value will be prorated out; the sum of the various rows will add up
      to the original value of the transaction.

    See https://github.com/iati-data-access/iati-flattener. The relevant code is in the ``process_package`` function
    of the ``FlattenIATIData`` class.
    """

    process_data()


@click.command()
@click.option('-s', 'start_at', default='', help="Filename to start processing at")
@click.option('-e', 'end_at', default='', help="Filename to end processing at")
@click.option('-f', 'force_update', is_flag=True, help="Update activities regardless of whether hashes have changed")
@click.option('-c', 'dont_update_codelists', is_flag=True, help="Don't update codelists")
@click.option('-a', 'dont_update_activities', is_flag=True, help="Don't update activities")
@with_appcontext
def update(start_at, end_at, force_update, dont_update_codelists, dont_update_activities):
    """Goes through the processed data (CSV files in output/csv) and inserts it into the iati_line DB table"""

    if not dont_update_codelists:
        import_codelists()

    if not dont_update_activities:
        import_activities_from_csvs(force_update=force_update)

    import_budgets_transactions_from_csvs(start_at_filename=start_at, end_at_filename=end_at)


@click.command()
@click.option('-s', 'start_at', default='', help="Filename to start processing at")
@click.option('-e', 'end_at', default='', help="Filename to end processing at")
@with_appcontext
def group(start_at, end_at):
    """Groups processed data into XLSX files for publication."""

    group_all(start_at, end_at)


@click.command()
@click.option('-s', 'start_at', default='', help="Filename to start processing at")
@click.option('-e', 'end_at', default='', help="Filename to end processing at")
@click.option('-f', 'force_update', is_flag=True, help="Update activities regardless of whether hashes have changed")
@with_appcontext
def update_activities_only(start_at, end_at, force_update):
    """Updates activity data only."""

    import_activities_from_csvs(start_at, end_at, force_update)
