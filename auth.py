import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import db_session
from .models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username or not password:
            error = 'To pole jest wymagane'
        # elif not password:
        #     error = 'password is required'
        elif (
                db_session.query(User)
                    .filter(User.username == username)
                    .one_or_none()
        ) is not None:
            error = 'Username {} is already registered'.format(username)

        if error is None:
            db_session.add(User(
                username=username,
                password=generate_password_hash(password)
            ))
            db_session.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = (
            db_session.query(User).filter(User.username == username)
                .one_or_none()
        )
        if user is None or not check_password_hash(user.password, password):
            error = 'Nieprawidłowa nazwa użytkownika lub hasło'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = (
            db_session.query(User).filter(User.id == user_id).one()
        )

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return wrapped_view