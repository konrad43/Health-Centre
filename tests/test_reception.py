
import pytest

from app.db import db_session
from app.models import Appointment


def del_patient(patient_name='Tomasz AA'):
    patient = db_session.query(Appointment)\
        .filter(Appointment.patient_name == patient_name).first()
    db_session.delete(patient)
    db_session.commit()


def test_index_not_log_in(client):
    response = client.get('/')
    assert response.status_code == 302


def test_incorrect_username(auth):
    res = auth.login('x','x')
    assert 'Nieprawidłowa nazwa użytkownika lub hasło' in res.data.decode('utf-8')


def test_index_logged_in(client, auth):
    auth.login()
    res = client.get('/')
    assert res.status_code == 200


def test_logout(auth):
    res = auth.logout()
    assert b'<title>Zaloguj</title>' in res.data


def test_add_commercial(client, auth):
    auth.login()
    res = client.post('/nowa-wizyta-komercyjna',
                      data=dict(patient_name='Tomasz AA',
                                doctor='dr Sapphira Richley',
                                service='psychologiczna',
                                price=300,
                                payment='G'),
                      follow_redirects=True)
    assert res.status_code == 200
    assert b'dr Sapphira Richley' in res.data
    assert b'Tomasz AA' in res.data

    del_patient('Tomasz AA')


def test_add_medicover(client, auth):
    auth.login()
    res = client.post('/nowa-wizyta-medicover',
                      data=dict(patient_name='Olek Medicover',
                                doctor='dr Ilysa Boulstridge',
                                service='psychologiczna',
                                referral=123465,
                                referral_accepted=True),
                      follow_redirects=True)
    assert res.status_code == 200
    assert b'dr Ilysa Boulstridge' in res.data
    assert b'Olek Medicover' in res.data

    del_patient('Olek Medicover')


def test_query_service(client, auth):
    auth.login()
    res = client.get(
        '/nowa-wizyta-komercyjna?doctor_name=dr+Jasper+Follis&service=lekarska'
    )
    assert b'<input name="doctor" class="form-control" ' \
           b'value="dr Jasper Follis">' in res.data
    assert b'<input type="text" class="form-control" ' \
           b'name="service" value="lekarska">' in res.data


def test_pricelist_no_args(client, auth):
    auth.login()
    res = client.get('/cennik')
    assert b'psychologiczna' and b'psychiatryczna' in res.data
    assert b'lekarska' and b'dietetyczna' and b'logopedyczna' in res.data


def test_pricelist_with_doctor_and_name(client, auth):
    auth.login()
    res = client.get(
        '/cennik?doctor_name=dr+Jarred+Beacon&service=psychologiczna'
    )
    assert b'dr Jarred Beacon' in res.data
    assert b'psychologiczna' in res.data

def test_pricelist_with_doctor(client, auth):
    auth.login()
    res = client.get(
        '/cennik?doctor_name=dr+Jarred+Beacon'
    )
    assert b'dr Jarred Beacon' in res.data
    assert b'psychologiczna' in res.data


def test_pricelist_with_name(client, auth):
    auth.login()
    res = client.get(
        '/cennik?doctor_name=&service=lekarska'
    )
    assert b'dr Jasper Follis' in res.data
    assert b'lekarska' in res.data
