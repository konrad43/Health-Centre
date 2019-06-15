import click
from .models import Base
from flask.cli import with_appcontext

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("sqlite:///app_db.db")

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(engine)


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized database.')


def init_app(app):
    # app.teardown_appcontext(db_session.remove())
    app.cli.add_command(init_db_command)