from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo

from flask.ext.babel import lazy_gettext


class RequiredIf(DataRequired):
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)

class Login(Form):
    email = StringField(lazy_gettext('E-Mail'), validators=[DataRequired(), Email()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
    remember_me = BooleanField(lazy_gettext('Remember password'))

class Register(Form):
    username = StringField(lazy_gettext('Username'), validators=[DataRequired()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
    email = StringField(lazy_gettext('E-Mail'), validators=[DataRequired(), Email()])

class Settings(Form):
    use_pushover = BooleanField(lazy_gettext('use pushover for notifications'))
    pushover_user = StringField(lazy_gettext('Pushover User-Token'), validators=[RequiredIf("use_pushover")])
    pushover_app = StringField(lazy_gettext('Pushover App-Token'), validators=[RequiredIf("use_pushover")])

class RegisterForm(Form):
    email = StringField(lazy_gettext('E-Mail'), validators=[DataRequired(), Email()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired(),EqualTo("password2")])
    password2 = PasswordField(lazy_gettext('Retype password'), validators=[DataRequired(),EqualTo("password")])