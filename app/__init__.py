import os

from flask import Flask
from flask_cors import CORS


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'strongside_stats.sqlite')
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    #ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .db import db
    db.init_app(app)

    from . import api
    app.register_blueprint(api.bp)

    from . import site
    app.register_blueprint(site.bp)
    app.add_url_rule('/', endpoint='index')

    from . import jinja_filters
    app.jinja_env.filters['seconds_to_minutes'] = jinja_filters.seconds_to_mins
    
    return app