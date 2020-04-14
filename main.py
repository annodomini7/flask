from flask import Flask, make_response, jsonify, redirect, render_template
from flask_restful import reqparse, abort, Api, Resource
from flask_login import current_user, LoginManager, logout_user, login_required, login_user
from data import db_session
from data.pharmacy import Pharmacy
from data.data import Data
from data.medicine import Medicine
from register_form import RegisterForm
from loginform import LoginForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)


@login_manager.user_loader
def load_user(pharmacy_id):
    session = db_session.create_session()
    return session.query(Pharmacy).get(pharmacy_id)


def main():
    db_session.global_init("db/pharmacy.db")
    # user = Pharmacy()
    # user.name = "Пользователь 1"
    # user.city = "биография пользователя 1"
    # user.address = "adasdad"
    # user.hours = "10-12"
    # user.set_password("qwertyuiopasdqw21321312")
    # session = db_session.create_session()
    # session.add(user)
    # session.commit()
    app.run()


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(Pharmacy).filter(Pharmacy.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = Pharmacy(
            name=form.name.data,
            city=form.city.data,
            address=form.address.data,
            hours=form.hours.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    main()
