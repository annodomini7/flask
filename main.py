from flask import Flask, make_response, jsonify, redirect, render_template
from flask_restful import reqparse, abort, Api, Resource
from flask_login import current_user, LoginManager, logout_user, login_required, login_user
from data import db_session
from data.pharmacy import Pharmacy
from data.data import Data
from data.medicine import Medicine
from register_form import RegisterForm
from login_form import LoginForm
from edit_form import EditForm
from random import shuffle

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


@app.route('/data/<int:pharmacy_id>', methods=['POST'])  # функция-обработчик поступающих json-запросов
def data_post(pharmacy_id):
    data = request.get_json()
    session = db_session.create_session()
    pharm = session.query(Pharmacy).get(pharmacy_id)
    if not pharm:
        return jsonify({'error': 404})
    if pharm.check_password(data["password"]) is False:
        return jsonify({'error': 403})
    for el in data["data"]:
        new = Data()
        new.pharmacy_id = pharmacy_id
        new.barcode = el["barcode"]
        new.cost = el["cost"]
        new.number = el["number"]
        session.add(new)
        session.commit()
    return jsonify({'success': 'OK'})


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(Pharmacy).filter(Pharmacy.name == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/profile')
@login_required
def profile():
    id = current_user.get_id()
    session = db_session.create_session()
    pharm = session.query(Pharmacy).filter(Pharmacy.id == id).first()
    return render_template('profile.html', title='Профиль', name=pharm.name, city=pharm.city, address=pharm.address,
                           hours=pharm.hours, phone=pharm.phone)


@app.route('/profile_edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    id = current_user.get_id()
    form = EditForm()
    if request.method == "GET":
        session = db_session.create_session()
        pharm = session.query(Pharmacy).filter(Pharmacy.id == id).first()
        if pharm:
            form.name.data = pharm.name
            form.city.data = pharm.city
            form.address.data = pharm.address
            form.hours.data = pharm.hours
            form.phone.data = pharm.phone
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        pharm = session.query(Pharmacy).filter(Pharmacy.id == id).first()
        if pharm:
            pharm.name = form.name.data
            pharm.city = form.city.data
            pharm.address = form.address.data
            pharm.hours = form.hours.data
            pharm.phone = form.phone.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('profile_edit.html', title='Редактирование профиля', form=form)


@app.route('/')
def main_screen():
    session = db_session.create_session()
    data = []
    pharmacy = session.query(Pharmacy).all()
    shuffle(pharmacy)
    for pharm in pharmacy[:10]:
        data.append({'name': pharm.name, 'city': pharm.city, 'address': pharm.address, 'hours': pharm.hours,
                     'phone': pharm.phone})

    return render_template('main_screen.html', title='Главная', data=data)


if __name__ == '__main__':
    main()
