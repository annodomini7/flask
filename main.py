from flask import Flask, jsonify, redirect, render_template
from flask_restful import abort, Api, request
from flask_login import current_user, LoginManager, logout_user, login_required, login_user
from data import db_session
from data.pharmacy import Pharmacy
from data.data import Data
from register_form import RegisterForm
from login_form import LoginForm
from edit_form import EditForm
import sqlite3

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)


def city_format(city):
    ch_map = {
        ord('\t'): ' ',
        ord('\n'): ' ',
        ord('\r'): None
    }
    # print(city.translate(ch_map).rstrip().capitalize())
    return city.translate(ch_map).rstrip().strip().capitalize()


@login_manager.user_loader
def load_user(pharmacy_id):
    db_session.global_init("db/pharmacy.db")
    session = db_session.create_session()
    return session.query(Pharmacy).get(pharmacy_id)


def main_site():
    db_session.global_init("db/pharmacy.db")
    app.run()


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_session.global_init("db/pharmacy.db")
        session = db_session.create_session()
        if session.query(Pharmacy).filter(Pharmacy.login == form.login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким логином существует. Придумайте другой логин")
        user = Pharmacy(
            name=form.name.data,
            city=city_format(form.city.data),
            address=form.address.data,
            hours=form.hours.data,
            phone=form.phone.data,
            region=request.form['region'],
            login=form.login.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        login_user(user)
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/data/<int:pharmacy_id>', methods=['POST'])  # функция-обработчик поступающих json-запросов
def data_post(pharmacy_id):
    data = request.get_json()
    db_session.global_init("db/pharmacy.db")
    session = db_session.create_session()
    pharm = session.query(Pharmacy).get(pharmacy_id)
    if not pharm:
        return jsonify({'error': 404})
    if pharm.check_password(data["password"]) is False:
        return jsonify({'error': 403})
    session.query(Data).filter(Data.pharmacy_id == pharmacy_id).delete()
    session.commit()
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
        db_session.global_init("db/pharmacy.db")
        session = db_session.create_session()
        user = session.query(Pharmacy).filter(Pharmacy.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, title='Авторизация')
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
    db_session.global_init("db/pharmacy.db")
    session = db_session.create_session()
    pharm = session.query(Pharmacy).filter(Pharmacy.id == id).first()
    return render_template('profile.html', title='Профиль', name=pharm.name, city=pharm.city,
                           address=pharm.address,
                           hours=pharm.hours, phone=pharm.phone, id=id, login=pharm.login,
                           region=pharm.region)


@app.route('/profile_edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    region = ''
    id = current_user.get_id()
    form = EditForm()
    if request.method == "GET":
        db_session.global_init("db/pharmacy.db")
        session = db_session.create_session()
        pharm = session.query(Pharmacy).filter(Pharmacy.id == id).first()
        if pharm:
            form.login.data = pharm.login
            form.name.data = pharm.name
            form.city.data = pharm.city
            form.address.data = pharm.address
            form.hours.data = pharm.hours
            form.phone.data = pharm.phone
            region = pharm.region
        else:
            abort(404)
    if form.validate_on_submit():
        db_session.global_init("db/pharmacy.db")
        session = db_session.create_session()
        if session.query(Pharmacy).filter(
                Pharmacy.login == form.login.data).first().id != current_user.get_id():
            return render_template('profile_edit.html', title='Редактирование профиля',
                                   form=form,
                                   message="Пользователь с таким логином существует. Придумайте другой логин")
        pharm = session.query(Pharmacy).filter(Pharmacy.id == id).first()
        if pharm:
            pharm.login = form.login.data
            pharm.name = form.name.data
            pharm.city = city_format(form.city.data)
            pharm.address = form.address.data
            pharm.hours = form.hours.data
            pharm.phone = form.phone.data
            pharm.region = request.form['region']
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('profile_edit.html', title='Редактирование профиля', form=form, region=region)


@app.route('/pharmacy/<city>')
def pharmacy_screen(city):
    db_session.global_init("db/pharmacy.db")
    session = db_session.create_session()
    data = []
    pharmacy = session.query(Pharmacy).filter(Pharmacy.city == city)
    for pharm in pharmacy:
        data.append({'name': pharm.name, 'address': pharm.address, 'hours': pharm.hours,
                     'phone': pharm.phone})

    return render_template('pharmacy_screen.html', title='Аптеки', data=data, city=city)


@app.route('/')
def main_screen():
    con = sqlite3.connect("db/pharmacy.db")
    cur = con.cursor()
    data = list(set(cur.execute(
        f"""select region
        from pharmacy""").fetchall()))
    data = sorted(list(map(lambda x: x[0], data)))
    header = 'Регионы, с которыми мы работаем'
    path = '/'
    return render_template('main_screen.html', title='Главная', data=data, header=header, path=path)


@app.route('/<region>')
def city_screen(region):
    con = sqlite3.connect("db/pharmacy.db")
    cur = con.cursor()
    data = list(set(cur.execute(
        f"""select city
        from pharmacy where region == '{region}'""").fetchall()))
    data = sorted(list(map(lambda x: x[0], data)))
    header = f'{region}: города, с которыми мы работаем'
    path = '/pharmacy/'
    return render_template('main_screen.html', title='Главная', data=data, header=header, path=path)


@app.route('/instruction')
def instruction():
    return render_template('instruction.html', title='Инструкция')


if __name__ == '__main__':
    main_site()
