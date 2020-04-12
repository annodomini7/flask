from flask import Flask, make_response, jsonify, redirect, render_template
from flask_restful import reqparse, abort, Api, Resource

from data import db_session
from data.pharmacy import Pharmacy
from data.data import Data
from data.medicine import Medicine
from register_form import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)


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
    # api.add_resource(users_resources.UsersListResource, '/api/v2/users')
    # api.add_resource(users_resources.UsersResource, '/api/v2/users/<int:user_id>')
    # api.add_resource(job_resources.JobsListResource, '/api/v2/jobs')
    # api.add_resource(job_resources.JobsResource, '/api/v2/jobs/<int:user_id>')
    #
    # @app.errorhandler(404)
    # def not_found(error):
    #     return make_response(jsonify({'error': 'Not found'}), 404)
    #
    # app.run(port=8080, host='127.0.0.1')


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
