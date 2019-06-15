from app.db import db_session
from app.models import Doctor


def test_add_doctor(client, auth):
    auth.login()
    res = client.post('/dodaj-specjaliste', data={'doctor': 'dr test'})
    assert 'Dodano nowego specjalistę' in res.data.decode('utf-8')

    data = db_session.query(Doctor).filter(Doctor.doctor_name == 'dr test')\
        .first()
    assert data
    db_session.delete(data)
    db_session.commit()