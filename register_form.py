from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField('Название аптеки*', validators=[DataRequired()])
    city = StringField("Город*")
    address = TextAreaField("Адрес*")
    hours = TextAreaField("Режим работы")
    phone = StringField("Номер телефона")
    password = PasswordField('Пароль*', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль*', validators=[DataRequired()])
    submit = SubmitField('Войти')
