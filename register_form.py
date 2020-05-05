from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField('Название аптеки', validators=[DataRequired()])
    region = StringField("Регион", validators=[DataRequired()])
    city = StringField("Город", validators=[DataRequired()])
    address = TextAreaField("Адрес", validators=[DataRequired()])
    hours = TextAreaField("Режим работы")
    phone = StringField("Номер телефона")
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
