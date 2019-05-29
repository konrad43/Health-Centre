import datetime

from flask import request, render_template
from sqlalchemy import func, and_

from .db import db_session
from .models import Appointment, Service, Doctor, PriceList

class FormQuery:
    """Get queries and returns data structure"""
    def __init__(self):
        self.doctors = db_session.query(Doctor)
        self.services = db_session.query(Service)
        self.payments = (
            db_session.query(Appointment)
                .group_by(Appointment.payment)
        )


def get_doctor_service_and_price(new_form):

    doctor_id = (
        db_session.query(Doctor.id)
            .filter(Doctor.doctor_name == new_form['doctor'])
    )
    service_id = (
        db_session.query(Service.id)
            .filter(Service.name == new_form['service'])
    )
    price_id = (
        db_session.query(PriceList.id).filter(and_(
                PriceList.doctor_id == doctor_id,
                PriceList.service_id == service_id)
    ))

    return dict(doctor_id=doctor_id, service_id=service_id, price_id=price_id)


def query_service(tab='commercial'):
    doctor = request.args.get('doctor_name')
    service = request.args.get('service')
    data = ''

    data_service = db_session.query(Service)
    data_doctor = db_session.query(Doctor)

    if doctor and service:
        doc_id = data_doctor.filter(Doctor.doctor_name == doctor).first()
        ser_id = data_service.filter(Service.name == service).first()
        data = (
            db_session.query(PriceList)
                .filter(and_(
                PriceList.doctor_id == doc_id.id,
                PriceList.service_id == ser_id.id
            )).first()
        )
    return render_template('reception/add_new.html',
                           data_doctor=data_doctor,
                           data_service=data_service,
                           doctor=doctor,
                           service=service,
                           data=data,
                           page='add',
                           tab=tab,
                           form_clear='reception.add_' + tab)


def date_to_datetime(form_name, timedelta=0):

    date = request.args.get(form_name)
    print('date: ', date)
    print('date type: ', type(date))

    try:
        date = list_date(date)
    except (ValueError, AttributeError):
        date = datetime.datetime.now() - datetime.timedelta(days=timedelta)
        date = list_date(date.strftime('%Y-%m-%d'))
        print('new date: ', date)
    return datetime.datetime(date[0],
                             date[1],
                             date[2]).strftime('%s')

def list_date(date):
    return list(map(int,date.split('-')))