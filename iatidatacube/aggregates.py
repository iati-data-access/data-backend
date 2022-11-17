from flask import Blueprint, request, Response
import json
from iatidatacube.extensions import db
from iatidatacube import models
import sqlalchemy as sa

class JSONEncoder(json.JSONEncoder):
    """ This encoder will serialize all entities that have a to_dict
    method by calling that method and serializing the result. """

    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, set):
            return [o for o in obj]
        if map_is_class and isinstance(obj, map):
            return [o for o in obj]
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)


def jsonify(obj, status=200, headers=None):
    """ Custom JSONificaton to support obj.to_dict protocol. """
    data = JSONEncoder().encode(obj)
    if 'callback' in request.args:
        cb = request.args.get('callback')
        data = '%s && %s(%s)' % (cb, cb, data)
    return Response(data, headers=headers, status=status,
                    mimetype='application/json')


blueprint = Blueprint('aggregates', __name__)

@blueprint.route('/spend_summary/')
def spend_summary():
    """
    Accepts arguments
      :: drilldown (e.g. 'recipient_country_or_region')
      :: drilldown_value (e.g. 'RW')
      :: years (e.g. '2020,2021')
    """
    drilldown = request.args.get('drilldown')
    drilldown_value = request.args.get(drilldown)
    years = request.args.get('calendar_year', '2021').split(",")
    aggregates = db.session.query(
        sa.func.sum(models.IATILine.value_usd).label('value_usd'),
        sa.func.sum(models.IATILine.value_eur).label('value_eur'),
        getattr(models.IATILine, drilldown).label('summary'),
        models.IATILine.calendar_year,
        models.IATILine.transaction_type
    ).filter(models.IATILine.calendar_year.in_(years)
    ).filter(getattr(models.IATILine, drilldown) == drilldown_value
    ).group_by(
        models.IATILine.calendar_year,
        getattr(models.IATILine, drilldown),
        models.IATILine.transaction_type
    ).all()
    cells = [{
        'value_usd': aggregate.value_usd,
        'value_eur': aggregate.value_eur,
        'summary': aggregate.summary,
        'calendar_year': aggregate.calendar_year,
        'transaction_type': aggregate.transaction_type
    } for aggregate in aggregates]
    return jsonify({
        'cells': cells,
    })


@blueprint.route('/by_country/')
def summary():
    """
    Accepts arguments
      :: drilldown (e.g. 'recipient_country_or_region')
      :: drilldown_value (e.g. 'RW')
      :: years (e.g. '2020,2021')
    """
    years = request.args.get('calendar_year', '2021').split(",")
    transaction_types = request.args.get('transaction_type', '3,4').split(",")
    aggregates = db.session.query(
        sa.func.sum(models.IATILine.value_usd).label('value_usd'),
        sa.func.sum(models.IATILine.value_eur).label('value_eur'),
        models.RecipientCountryorRegion.code,
        models.RecipientCountryorRegion.name_en,
        models.IATILine.calendar_year
    ).join(models.RecipientCountryorRegion
    ).filter(models.IATILine.calendar_year.in_(years)
    ).filter(models.IATILine.transaction_type.in_(transaction_types)
    ).group_by(
        models.RecipientCountryorRegion.code,
        models.RecipientCountryorRegion.name_en,
        models.IATILine.calendar_year
    ).all()
    cells = [{
        'value_usd': aggregate.value_usd,
        'value_eur': aggregate.value_eur,
        'code': aggregate.code,
        'name_en': aggregate.name_en,
        'calendar_year': aggregate.calendar_year
    } for aggregate in aggregates]
    return jsonify({
        'cells': cells,
    })


@blueprint.route('/by_country/')
def summary_country():
    """
    Accepts arguments
      :: drilldown (e.g. 'recipient_country_or_region')
      :: drilldown_value (e.g. 'RW')
      :: years (e.g. '2020,2021')
    """
    years = request.args.get('calendar_year', '2021').split(",")
    transaction_types = request.args.get('transaction_type', '3,4').split(",")
    aggregates = db.session.query(
        sa.func.sum(models.IATILine.value_usd).label('value_usd'),
        sa.func.sum(models.IATILine.value_eur).label('value_eur'),
        models.RecipientCountryorRegion.code,
        models.RecipientCountryorRegion.name_en,
        models.IATILine.calendar_year
    ).join(models.RecipientCountryorRegion
    ).filter(models.IATILine.calendar_year.in_(years)
    ).filter(models.IATILine.transaction_type.in_(transaction_types)
    ).group_by(
        models.RecipientCountryorRegion.code,
        models.RecipientCountryorRegion.name_en,
        models.IATILine.calendar_year
    ).all()
    cells = [{
        'value_usd': aggregate.value_usd,
        'value_eur': aggregate.value_eur,
        'code': aggregate.code,
        'name_en': aggregate.name_en,
        'calendar_year': aggregate.calendar_year
    } for aggregate in aggregates]
    return jsonify({
        'cells': cells,
    })


@blueprint.route('/by_provider/')
def summary_provider():
    """
    Accepts arguments
      :: drilldown (e.g. 'recipient_country_or_region')
      :: drilldown_value (e.g. 'RW')
      :: years (e.g. '2020,2021')
    """
    years = request.args.get('calendar_year', '2021').split(",")
    transaction_types = request.args.get('transaction_type', '3,4').split(",")
    aggregates = db.session.query(
        sa.func.sum(models.IATILine.value_usd).label('value_usd'),
        sa.func.sum(models.IATILine.value_eur).label('value_eur'),
        models.ReportingOrganisation.code,
        models.ReportingOrganisation.name_en,
        models.IATILine.calendar_year
    ).join(models.ReportingOrganisation
    ).filter(models.IATILine.calendar_year.in_(years)
    ).filter(models.IATILine.transaction_type.in_(transaction_types)
    ).group_by(
        models.ReportingOrganisation.code,
        models.ReportingOrganisation.name_en,
        models.IATILine.calendar_year
    ).order_by(
        sa.desc('value_usd')
    ).all()
    cells = [{
        'value_usd': aggregate.value_usd,
        'value_eur': aggregate.value_eur,
        'code': aggregate.code,
        'name_en': aggregate.name_en,
        'calendar_year': aggregate.calendar_year
    } for aggregate in aggregates]
    return jsonify({
        'cells': cells,
    })


@blueprint.route('/by_sector/')
def summary_sector():
    """
    Accepts arguments
      :: drilldown (e.g. 'recipient_country_or_region')
      :: drilldown_value (e.g. 'RW')
      :: years (e.g. '2020,2021')
    """
    years = request.args.get('calendar_year', '2021').split(",")
    transaction_types = request.args.get('transaction_type', '3,4').split(",")
    aggregates = db.session.query(
        sa.func.sum(models.IATILine.value_usd).label('value_usd'),
        sa.func.sum(models.IATILine.value_eur).label('value_eur'),
        models.SectorCategory.code,
        models.SectorCategory.name_en,
        models.IATILine.calendar_year
    ).join(models.SectorCategory
    ).filter(models.IATILine.calendar_year.in_(years)
    ).filter(models.IATILine.transaction_type.in_(transaction_types)
    ).group_by(
        models.SectorCategory.code,
        models.SectorCategory.name_en,
        models.IATILine.calendar_year
    ).order_by(
        sa.desc('value_usd')
    ).all()
    cells = [{
        'value_usd': aggregate.value_usd,
        'value_eur': aggregate.value_eur,
        'code': aggregate.code,
        'name_en': aggregate.name_en,
        'calendar_year': aggregate.calendar_year
    } for aggregate in aggregates]
    return jsonify({
        'cells': cells,
    })
