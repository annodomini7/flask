from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError
import phonenumbers


class EditForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    name = StringField('Название аптеки', validators=[DataRequired()])
    city = StringField("Город", validators=[DataRequired()])
    address = TextAreaField("Адрес", validators=[DataRequired()])
    hours = TextAreaField("Режим работы")
    phone = StringField("Номер телефона")
    submit = SubmitField('Сохранить изменения')

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')
