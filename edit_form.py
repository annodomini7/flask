from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class EditForm(FlaskForm):
    name = StringField('Название аптеки*', validators=[DataRequired()])
    city = StringField("Город*", validators=[DataRequired()])
    address = TextAreaField("Адрес*", validators=[DataRequired()])
    hours = TextAreaField("Режим работы")
    phone = StringField("Номер телефона")
    submit = SubmitField('Сохранить изменения')
