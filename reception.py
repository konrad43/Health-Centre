from flask import (
    Blueprint, abort, render_template, request, jsonify, redirect, url_for, g
)
from .db import db_session
from .models import Base, Appointment, Service, Doctor, PriceList
import datetime
from sqlalchemy import func, and_

bp = Blueprint('reception', __name__)


@bp.route('/', methods=('GET',))
def index():
    start_date = date_to_datetime(None, 0)
    visits = (
        db_session.query(Appointment)
            .filter(func.strftime('%s', Appointment.date) >= start_date)
            .all()
    )
    if visits:
        return render_template('reception/visits.html',
                               visits=visits,
                               page='home')
    else:
        return 'Brak wizyt'


@bp.route('/<int:id>', methods=('GET', 'PUT'))
def update(id):
    if request.method == 'PUT':
        pass
    else:
        data = (
            db_session.query(Appointment)
                .filter(Appointment.id == id).one_or_none()
        )
        return render_template('reception/update.html', data=data)


@bp.route('/nowa-wizyta-komercyjna', methods=('GET', 'POST'))
def add_commercial():
    if request.method == 'POST':

        new_form = request.form
        err = None

        if not new_form:
            err = 'This fields is required!'
        else:
            data_form = get_doctor_service_and_price(new_form)
            db_session.add(Appointment(
                patient_name=new_form['patient_name'],
                doctor_id=data_form['doctor_id'],
                service_id=data_form['service_id'],
                price_id=data_form['price_id'],
                payment=new_form['payment']
            ))
            # db_session.add(Appointment(name=name))
            db_session.commit()
            print('zapisano')
            # return redirect(url_for('index'))
            return f'{request.form}'
    else:
        return query_service()


@bp.route('/nowa-wizyta-medicover', methods=('GET', 'POST'))
def add_medicover():
    if request.method == 'POST':
        new_form = request.form
        data_form = get_doctor_service_and_price(new_form)
        db_session.add(Appointment(
            patient_name=new_form['patient_name'],
            doctor_id=data_form['doctor_id'],
            service_id=data_form['service_id'],
            payment='Medicover',
            referral=new_form['referral'],
            referral_accepted=new_form['referral_accepted']
        ))
        db_session.commit()
        return redirect(url_for('index'))
    else:
        return query_service('medicover')


@bp.route('/nowa-wizyta-pzu', methods=('GET', 'POST'))
def add_pzu():
    if request.method == 'POST':
        pass
    else:
        return query_service('pzu')


@bp.route('/edytuj-cennik')
def edit_pricelist():
    pass


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
                           tab=tab)


@bp.route('/szukaj', methods=('GET', 'POST'))
def search_data():
    if request.method == 'GET':
        name = request.args.get('name')
        dates = request.args
        # print(dates)
        # print('name: ', name)
        start_date = date_to_datetime('start_date', 30)
        # print('start_date: ', start_date)
        try:
            end_date = date_to_datetime('end_date', -1)
            # print('end_date: ', end_date)
        except:
            # print('brak daty końcowej')
            end_date = None

        if end_date:
            data = (
                db_session.query(Appointment)
                    .filter(and_(
                    func.strftime('%s', Appointment.date) >= start_date,
                    func.strftime('%s', Appointment.date) <= end_date
                ))
            )
        else:
            data = (
                db_session.query(Appointment)
                    .filter( func.strftime('%s', Appointment.date) >= start_date)
            )

        if name:
            data = data.filter(Appointment.patient_name.like(f'{name}%'))
        else:
            name = ''


        data_all = data.all()
        patient_sum = len(data_all)
        # print(data.first().price.price)
        revenue = 0
        for i in data_all:
            try:
                revenue += i.price.price
            except AttributeError:
                pass
        # print('Przychód: ', revenue)

        return render_template('reception/search.html', visits=data,
                               start_date=dates.get('start_date'),
                               end_date=dates.get('end_date'),
                               name=name,
                               patient_sum=patient_sum,
                               revenue=revenue,
                               page='search')

    return render_template('reception/search.html')


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
