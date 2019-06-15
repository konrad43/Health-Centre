from sqlalchemy import and_

from app.db import db_session
from app.models import Doctor, Service, PriceList
from app.my_func import FormQuery


def test_add_doctor(client, auth):
    auth.login()
    res = client.post('/dodaj-specjaliste', data={'doctor': 'dr test'})
    assert 'Dodano nowego specjalistę' in res.data.decode('utf-8')

    data = db_session.query(Doctor).filter(Doctor.doctor_name == 'dr test')\
        .first()
    assert data
    db_session.delete(data)
    db_session.commit()


def test_add_service(client, auth):
    auth.login()
    res = client.post('/dodaj-usluge', data={'service': 'service test'})
    assert 'Dodano nową usługę' in res.data.decode('utf-8')

    data = db_session.query(Service).filter(Service.name == 'service test')\
        .first()
    assert data
    db_session.delete(data)
    db_session.commit()


def test_add_price(client, auth):
    auth.login()
    res = client.post('/dodaj-cene', data={'doctor_name': 'dr Jasper Follis',
                                          'service': 'lekarska',
                                          'price': 150})
    assert 'Dodano nową cenę' in res.data.decode('utf-8')

    form_query = FormQuery()
    data = (
        db_session.query(PriceList)
                .filter(and_(
            PriceList.service_id == 3,
            PriceList.doctor_id == 4
        )).first()
    )
    assert data
    db_session.delete(data)
    db_session.commit()