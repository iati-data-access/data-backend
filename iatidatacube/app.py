from flask import Flask, request, Response, send_file, make_response, jsonify
from sqlalchemy import create_engine
from babbage.manager import JSONCubeManager
from babbage.api import configure_api
from flask_cors import CORS
from iatidatacube.aggregates import blueprint as aggregates_blueprint
from iatidatacube import extensions, commands, xlsx_writer


def create_app(config_object='config'):
    app = Flask(__name__.split('.', maxsplit=1)[0])
    app.config.from_object(config_object)
    CORS(app)
    extensions.db.init_app(app)
    extensions.migrate.init_app(app, extensions.db)
    register_commands(app)
    register_blueprints(app)
    register_responses(app)
    return app

def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.setup_codelists)
    app.cli.add_command(commands.drop_all)
    app.cli.add_command(commands.update)
    app.cli.add_command(commands.download)
    app.cli.add_command(commands.process)
    app.cli.add_command(commands.group)
    app.cli.add_command(commands.update_activities_only)

def register_blueprints(app):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    models_directory = 'models/'
    # FIXME later change this to CachingJSONCubeManager
    manager = JSONCubeManager(engine, models_directory)
    blueprint = configure_api(app, manager)
    app.register_blueprint(blueprint, url_prefix='/api/babbage')
    app.register_blueprint(aggregates_blueprint, url_prefix='/api/aggregates')


def register_responses(app):
    @app.after_request
    def handle_xlsx(response):
        if request.args.get('format') == 'xlsx':
            response_json = response.get_json(force=True)
            if 'cells' in response_json:
                data = list(xlsx_writer.serialise(request.args, response_json['cells']))
            else:
                data = response_json['data']
            if len(data) >= 1048576:
                return make_response(jsonify(msg="Your requested file contains too many rows to create an Excel file. Narrow your search filters and try again."), 400)
            xlsx_file = xlsx_writer.generate_xlsx(data)
            response = make_response(send_file(xlsx_file,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='data.xlsx'))
        return response
