import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'strongside_stats.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # imports
    from . import db
    db.init_app(app)

    from . import site
    app.register_blueprint(site.bp)
    app.add_url_rule('/', endpoint='index')

    from .jinja_filters import date, game_length
    app.add_template_filter(date)
    app.add_template_filter(game_length)

    return app