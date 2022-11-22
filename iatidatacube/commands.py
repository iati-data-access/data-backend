"""Click commands."""
import click
from flask.cli import with_appcontext
from iatidatacube.import_data import import_country, setup_db, drop_db, import_all, fetch_data, process_data
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
    drop_db()


@click.command()
@click.option('-s', 'start_at', default='')
@click.option('-e', 'end_at', default='')
@with_appcontext
def update(start_at, end_at):
    """Updates all processed data."""
    import_all(start_at, end_at)


@click.command()
@with_appcontext
def download():
    """Downloads all data."""
    fetch_data()


@click.command()
@with_appcontext
def process():
    """Processes all data."""
    process_data()
