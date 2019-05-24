import datetime

from flask import (
    Blueprint, abort, render_template, request, jsonify, redirect, url_for, g
)
from sqlalchemy import func, and_

from .db import db_session
from .models import Base, Appointment, Service, Doctor, PriceList
from .my_func import (
FormQuery, get_doctor_service_and_price, query_service, date_to_datetime
)

bp = Blueprint('reception', __name__)


@bp.route('/', methods=('GET',))
def index():
    start_date = date_to_datetime(None, 0)
    visits = (
        db_session.query(Appointment)
            .filter(func.strftime('%s', Appointment.date) >= start_date)
            .all()
    )
    return render_template('reception/visits.html',
                               visits=visits,
                               page='home')


@bp.route('/<int:id>', methods=('GET', 'POST'))
def update(id):
    data = (
        db_session.query(Appointment)
            .filter(Appointment.id == id).one_or_none()
    )

    if request.method == 'POST':
        new_form = request.form
        data_form = get_doctor_service_and_price(new_form)

        data.patient_name = new_form['patient_name']
        data.doctor_id = data_form['doctor_id']
        data.service_id = data_form['service_id']
        data.price_id = data_form['price_id']
        data.payment=new_form['payment']

        try:
            data.referral=new_form['referral']
            data.referral_accepted=new_form['referral_accepted']
        except KeyError:
            pass

        db_session.add(data)
        db_session.commit()

    return render_template('reception/update.html', data=data, form=FormQuery())


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
                payment=new_form['payment'],
            ))
            db_session.commit()
            print('zapisano')
            return redirect(url_for('index'))
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

@bp.route('/cennik')
def pricelist():

    form_query = FormQuery()
    pricelist = db_session.query(PriceList)
    return render_template('reception/pricelist.html', page='price',
                           price=pricelist, data_doctor=form_query.doctors,
                           data_service=form_query.services)


@bp.route('/szukaj', methods=('GET', 'POST'))
def search_data():
    if request.method == 'GET':
        name = request.args.get('name')
        dates = request.args
        doctor = request.args.get('doctor')
        payment = request.args.get('payment')
        start_date = date_to_datetime('start_date', 30)
        try:
            end_date = date_to_datetime('end_date', -1)
        except:
            end_date = None

        # Query dates
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

        # Query patient name
        if name:
            data = data.filter(Appointment.patient_name.like(f'{name}%'))
        else:
            name = ''

        # Query doctor name
        if doctor:
            doctor_id = (
                db_session.query(Doctor.id)
                    .filter(Doctor.doctor_name.like(f'{doctor}'))
            )
            data = data.filter(Appointment.doctor_id == doctor_id)
        else:
            doctor = ''

        # Query payment method
        if payment:
            data = data.filter(Appointment.payment.like(f'{payment}'))
        else:
            payment = ''

        # Print extra info
        data_all = data.all()
        patient_sum = len(data_all)
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
                               doctor=doctor,
                               payment=payment,
                               patient_sum=patient_sum,
                               revenue=revenue,
                               page='search')

    return render_template('reception/search.html')


