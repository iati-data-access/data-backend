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
    #FIXME support more languages later
    lang = 'en'
    keys = data[0].keys()
    drilldowns = args.get('drilldown').split('|')
    aggregates = args.get('aggregates').split('|')
    model = current_app.extensions['babbage'].get_cube_model('iatiline')
    dimensions = model['dimensions']
    measures = model['measures']
    rollup, _rollup_values = args.get('rollup', ':[]').split(':')
    rollup_values = json.loads(_rollup_values)

    for row in data:
        _l = {}
        for drilldown in drilldowns:
            # Dimensions look a bit different in different cases
            if drilldown in dimensions:
                _attributes = dimensions.get(drilldown)['attributes']
                if (f'name_{lang}' in _attributes) and ('code' in _attributes):
                    _l[dimensions.get(drilldown)['label']] = row.get(f"{drilldown}.code") + " - " + row.get(f"{drilldown}.name_{lang}")
                elif (f'name_{lang}' in _attributes):
                    _l[dimensions.get(drilldown)['label']] = row.get(f"{drilldown}.name_{lang}")
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
                #FIXME improve handling of rollups; need to find labels from database
                for rollup_value in rollup_values:
                    r_key = '-'.join(rollup_value)
                    r_label = {'3-4': 'Spending', 'budget': 'Budget'}.get(r_key, r_key)
                    _l[f"{measures.get(_measure)['label']} ({r_label})"] = row.get(f"{aggregate}_{r_key}")
        yield _l
