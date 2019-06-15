

import pytest

from app.db import db_session
from app.my_func import date_to_datetime


def test_index_not_log_in(client):
    response = client.get('/')
    assert response.status_code == 302


def test_incorrect_username(client, auth):
    res = auth.login('x','x')
    assert 'Nieprawidłowa nazwa użytkownika lub hasło' in res.data.decode('utf-8')


def test_index_logged_in(client, auth, app):
    rv = auth.login()
    # rv = login(client, app.config['USERNAME'], 'test')
    res = client.get('/')
    assert res.status_code == 200


def test_logout(auth):
    res = auth.logout()
    assert b'<title>Zaloguj</title>' in res.data





