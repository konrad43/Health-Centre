import os
import tempfile

import pytest

from app import create_app
from app.db import init_db, db_session
from app.models import User


@pytest.fixture
def app():
    app = create_app({'TESTING': True})
    return app

#
# @pytest.fixture
# def client(app):
#     return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password},
            follow_redirects=True
        )

    def logout(self):
        return self._client.get('/auth/logout', follow_redirects=True
)


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def client(app):
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    client = app.test_client()

    app.config['USERNAME'] = 'test'
    app.config['PASSWORD'] = 'test'

    with app.app_context():
        if not db_session.query(User)\
                    .filter(User.username == 'test').one_or_none():
            init_db()
            db_session.add(User(
                username='test',
                password='pbkdf2:sha256:150000$l7pCcedE$2a6ac9df6a45af1a4b50c76f317a078a24577843c3d79c4e29f600f3bef61e8c',
            ))
            db_session.commit()

    yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

