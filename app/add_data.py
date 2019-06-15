from flask import Blueprint, render_template, request, flash

from .db import db_session
from .auth import login_required
from .my_func import FormQuery
from .models import Doctor, Service, PriceList

bp = Blueprint('add_data', __name__)


@bp.route('/dodaj-specjaliste', methods=('GET', 'POST'))
@login_required
def add_doctor():
    if request.method == 'POST':
        db_session.add(Doctor(doctor_name=request.form['doctor']))
        db_session.commit()
        flash('Dodano nowego specjalistę')

    return render_template('add_data/add_data.html', tab='doctor')


@bp.route('/dodaj-usluge', methods=('GET', 'POST'))
@login_required
def add_service():
    if request.method == 'POST':
        db_session.add(Service(name=request.form['service']))
        db_session.commit()
        flash('Dodano nową usługę')

    return render_template('add_data/add_data.html', tab='service')


@bp.route('/dodaj-cene', methods=('GET', 'POST'))
@login_required
def add_price():
    if request.method == 'POST':
        form = request.form
        data_form = FormQuery()
        db_session.add(PriceList(
            doctor_id=data_form.get_doctor_id(form['doctor_name']),
            service_id=data_form.get_service_id(form['service']),
            price=form['price']
        ))
        db_session.commit()
        flash('Dodano nową cenę do cennika')

    return render_template('add_data/add_data.html', tab='price',
                           data_form=FormQuery())
