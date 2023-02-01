"""Click commands."""
import click
from flask.cli import with_appcontext
from iatidatacube.import_data import import_country, setup_db, drop_db, import_all, fetch_data, process_data, group_all
from iatidatacube.import_codelists import import_codelists


@click.command()
@with_appcontext
def setup_codelists():
    """Create database and setup codelists."""
    setup_db()
    import_codelists()


@click.command()
@with_appcontext
def drop_all():
    """Drops all table from the database."""
    if click.confirm("Are you sure you would like to drop all data in the database? This action cannot be undone!"):
        print("Dropping DB.")
        drop_db()
    else:
        print("Aborting.")


@click.command()
@with_appcontext
def download():
    """Downloads all data."""
    fetch_data()


@click.command()
@with_appcontext
def process():
    """Processes all data into CSV files using IATI Flattener."""
    process_data()


@click.command()
@click.option('-s', 'start_at', default='')
@click.option('-e', 'end_at', default='')
@with_appcontext
def update(start_at, end_at):
    """Updates all processed data."""
    import_all(start_at, end_at)


@click.command()
@click.option('-s', 'start_at', default='')
@click.option('-e', 'end_at', default='')
@with_appcontext
def group(start_at, end_at):
    """Groups processed data into XLSX files for publication."""
    group_all(start_at, end_at)
