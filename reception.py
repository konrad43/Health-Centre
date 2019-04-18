from flask import (
    Blueprint, abort, render_template, request, jsonify, redirect, url_for
)
from .db import db_session
from .models import Base, Appointment
import datetime
from sqlalchemy import func, and_

bp = Blueprint('reception', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        data = request.json.get('name')
        print(data)
        db_session.add(Appointment(name=data))
        db_session.commit()
        print('zapisano w bazie')
        return 'zapisano'

    else:
        visits = (
            db_session.query(Appointment.name, Appointment.appointment_id, Appointment.date)
                .all()
        )
        print(visits[0][2].strftime('%H:%M %d.%m.%Y'))
        return render_template('reception/visits.html', visits=visits)

@bp.route('/nowa_wizyta', methods=('GET', 'POST'))
def add_appoint():
    if request.method == 'POST':
        name = request.form['name']
        err = None

        if not name:
            err = 'This fields is required!'
        else:
            db_session.add(Appointment(name=name))
            db_session.commit()
            print('zapisano')
            return redirect(url_for('index'))
    else:
        return render_template('reception/add_new.html')

@bp.route('/szukaj', methods=('GET', 'POST'))
def search_data():
    if request.method == 'GET':
        name = request.args.get('name')
        dates = request.args
        print(dates)
        print('name: ', name)
        start_date = date_to_datetime('start_date', 30)
        print('start_date: ', start_date)
        try:
            end_date = date_to_datetime('end_date', -1)
            print('end_date: ', end_date)
        except:
            print('brak daty końcowej')
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
            data = data.filter(Appointment.name.like(f'{name}%'))
        # print(data)
        return render_template('reception/search.html', visits=data,
                               start_date=dates.get('start_date'),
                               end_date=dates.get('end_date'),
                               name=name)

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
