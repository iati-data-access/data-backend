from pyexcelerate import Workbook
from io import BytesIO
from flask import current_app
import json

def generate_xlsx(data):
    output = BytesIO()
    wb = Workbook()
    data_list = [list(data[0].keys())]+[row.values() for row in data]
    wb.new_sheet("Data", data=data_list)
    wb.save(output)
    output.seek(0)
    return output


def serialise(args, data):
    lang = args.get('lang', 'en')
    keys = data[0].keys()
    drilldowns = args.get('drilldown').split('|')
    aggregates = args.get('aggregates', 'value_usd.sum').split('|')
    babbage = current_app.extensions['babbage']
    model = babbage.get_cube_model('iatiline')
    dimensions = model['dimensions']
    measures = model['measures']
    rollup, _rollup_values = args.get('rollup', ':[]').split(':')
    rollup_values = json.loads(_rollup_values)
    if rollup:
        if ('.' in rollup) and (rollup.split('.')[0] in dimensions):
            _r_dimension, _r_attribute = rollup.split('.')
        else:
            _r_dimension = rollup
        get_rollup_values_from_db = babbage.get_cube('iatiline').members(_r_dimension)
        rollup_values_from_db = dict([(t[f'{_r_dimension}.code'],
            t[f'{_r_dimension}.name_{lang}']) for t in get_rollup_values_from_db['data']])

    for row in data:
        _l = {}
        for drilldown in drilldowns:
            # Dimensions look a bit different in different cases
            if drilldown in dimensions:
                _attributes = dimensions.get(drilldown)['attributes']
                if (f'name_{lang}' in _attributes) and ('code' in _attributes):
                    _l[_attributes[f'name_{lang}']['label']] = row.get(f"{drilldown}.code") + " - " + row.get(f"{drilldown}.name_{lang}")
                elif (f'name_{lang}' in _attributes):
                    _l[_attributes[f'name_{lang}']['label']] = row.get(f"{drilldown}.name_{lang}")
                elif ('code' in _attributes):
                    _l[dimensions.get(drilldown)['label']] = row.get(f"{drilldown}.code")
            elif ('.' in drilldown) and (drilldown.split('.')[0] in dimensions):
                _dimension, _attribute = drilldown.split('.')
                _l[dimensions.get(_dimension)['attributes'].get(_attribute)['label']] = row.get(drilldown)
        for aggregate in aggregates:
            _measure, _agg = aggregate.split(".")
            if rollup == '':
                _l[measures.get(_measure)['label']] = row.get(aggregate)
            else:
                for rollup_value in rollup_values:
                    r_key = '-'.join(rollup_value)
                    r_label = ", ".join([rollup_values_from_db.get(rollup_value_item) for rollup_value_item in rollup_value])
                    _l[f"{measures.get(_measure)['label']} ({r_label})"] = row.get(f"{aggregate}_{r_key}")
        yield _l
