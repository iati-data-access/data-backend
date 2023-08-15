"""Click commands."""
import click
from flask.cli import with_appcontext
from iatidatacube.import_data import setup_db, drop_db, import_all, fetch_data, process_data, group_all, import_all_activities
from iatidatacube.import_codelists import import_codelists


@click.command()
@with_appcontext
def setup_codelists():
    """Create database and setup codelists."""
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
@click.option('-s', 'start_at', default='', help="Filename to start processing at")
@click.option('-e', 'end_at', default='', help="Filename to end processing at")
@click.option('-f', 'force_update', is_flag=True, help="Update activities regardless of whether hashes have changed")
@click.option('-c', 'dont_update_codelists', is_flag=True, help="Don't update codelists")
@click.option('-a', 'dont_update_activities', is_flag=True, help="Don't update activities")
@with_appcontext
def update(start_at, end_at, force_update,
        dont_update_codelists, dont_update_activities):
    """Updates all processed data."""
    if not(dont_update_codelists):
        import_codelists()
    import_all(start_at=start_at, end_at=end_at,
        langs=['en', 'fr', 'es', 'pt'],
        force_update=force_update,
        update_activities=not(dont_update_activities))


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
    import_all_activities(start_at, end_at, force_update)
