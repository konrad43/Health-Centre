import os
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE =os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass



    from . import db, reception
    db.init_app(app)
    # app.register_blueprint(auth.bp)
    app.register_blueprint(reception.bp)

    app.add_url_rule('/', endpoint='index')

    # from .db import db_session
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.db_session.remove()

    return app


# export FLASK_APP=app
# export FLASK_ENV=development
# flask run