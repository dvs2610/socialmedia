from wtforms import DateField, StringField, PasswordField, TextAreaField, validators
from flask_wtf import FlaskForm

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=10)], render_kw={"placeholder": "Pick your own unique username"})
    password = PasswordField('Password', [
		validators.Length(min=8, max=32),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords don\'t match.')
    ], render_kw={"placeholder": "Create a password"})
    confirm = PasswordField('Confirm Password', render_kw={"placeholder": "Repeat your password"})
    birthday = DateField('Birthday', render_kw={"placeholder": "Birthday"})
    fullname = StringField('Full name', [validators.Length(max=60)], render_kw={"placeholder": "Full name"})
    location = StringField('Location', [validators.Length(max=80)], render_kw={"placeholder": "Location"})
    bio = StringField('Something fun', [validators.Length(max=120)], render_kw={"placeholder": "Fun facts!"})


class LoginForm(FlaskForm):
	username = StringField('Username', [validators.DataRequired()], render_kw={"placeholder": "Username"})
	password = PasswordField('Password', [validators.DataRequired()], render_kw={"placeholder": "Password"})


class PostForm(FlaskForm):
    content = TextAreaField(
        '',
        validators=[validators.DataRequired(), validators.Length(max=5000)],
        render_kw={"placeholder": "Write a post..."}
    )
