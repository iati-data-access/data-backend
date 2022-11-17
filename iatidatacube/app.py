from flask import Flask
from sqlalchemy import create_engine
from babbage.manager import JSONCubeManager
from babbage.api import configure_api
from flask_cors import CORS
from iatidatacube.aggregates import blueprint as aggregates_blueprint
from iatidatacube import extensions, commands



def create_app(config_object='config'):
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    CORS(app)
    extensions.db.init_app(app)
    app.cli.add_command(commands.setup_country)
    app.cli.add_command(commands.setup_codelists)
    app.cli.add_command(commands.drop_all)
    app.cli.add_command(commands.update)
    app.cli.add_command(commands.download)
    app.cli.add_command(commands.process)
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    models_directory = 'models/'
    manager = JSONCubeManager(engine, models_directory)
    blueprint = configure_api(app, manager)
    app.register_blueprint(blueprint, url_prefix='/api/babbage')
    app.register_blueprint(aggregates_blueprint, url_prefix='/api/aggregates')
    return app
