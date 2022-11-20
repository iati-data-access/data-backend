from flask import Flask, request, Response, send_file, make_response
from sqlalchemy import create_engine
from babbage.manager import JSONCubeManager
from babbage.api import configure_api
from flask_cors import CORS
from iatidatacube.aggregates import blueprint as aggregates_blueprint
from iatidatacube import extensions, commands, xlsx_writer


def create_app(config_object='config'):
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    CORS(app)
    extensions.db.init_app(app)
    register_commands(app)
    register_blueprints(app)
    register_responses(app)
    return app

def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.setup_country)
    app.cli.add_command(commands.setup_codelists)
    app.cli.add_command(commands.drop_all)
    app.cli.add_command(commands.update)
    app.cli.add_command(commands.download)
    app.cli.add_command(commands.process)

def register_blueprints(app):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    models_directory = 'models/'
    manager = JSONCubeManager(engine, models_directory)
    blueprint = configure_api(app, manager)
    app.register_blueprint(blueprint, url_prefix='/api/babbage')
    app.register_blueprint(aggregates_blueprint, url_prefix='/api/aggregates')


def register_responses(app):
    @app.after_request
    def handle_xlsx(response):
        if request.args.get('format') == 'xlsx':
            data = response.get_json()['cells']
            xlsx_file = xlsx_writer.generate_xlsx(data)
            print("made xlsx file", xlsx_file)
            response = make_response(send_file(xlsx_file,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='data.xlsx'))
        return response
