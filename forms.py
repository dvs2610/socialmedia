from datetime import date
from wtforms import DateField, StringField, PasswordField, TextAreaField, ValidationError, validators, FileField
from flask_wtf import FlaskForm

def validate_username(_form, field):
     if len(field.data) < 4 or len(field.data) > 30:
          raise ValidationError("Username must be between 4 and 30 characters long.")

def validate_password(_form, field):
     if len(field.data) < 8 or len(field.data) > 48:
          raise ValidationError("Password must be between 8 and 48 characters long.")

def validate_confirm(form, field):
     if field.data != form.password.data:
          raise ValidationError("Passwords don't match.")

def validate_birthday(_form, field):
     if field.data and field.data < date(1900, 1, 1):
          raise ValidationError("Birthday cannot be before 01-01-1900.")

def validate_fullname(_form, field):
     if len(field.data) > 100:
          raise ValidationError("Full name should not exceed 100 characters.")

def validate_location(_form, field):
     if len(field.data) > 100:
          raise ValidationError("Location should not exceed 100 characters.")

def validate_bio(_form, field):
     if len(field.data) > 200:
          raise ValidationError("Bio should not exceed 200 characters.")


class RegistrationForm(FlaskForm):
    username = StringField('Username', [validate_username], render_kw={"placeholder": "Pick your own unique username"})
    password = PasswordField('Password', [validate_password], render_kw={"placeholder": "Create a password"})
    confirm = PasswordField('Confirm Password', [validate_confirm], render_kw={"placeholder": "Repeat your password"})
    birthday = DateField('Birthday', validators=[validators.Optional(), validate_birthday], render_kw={"placeholder": "Birthday"})
    fullname = StringField('Full name', [validate_fullname], render_kw={"placeholder": "Full name"})
    location = StringField('Location', [validate_location], render_kw={"placeholder": "Location"})
    bio = StringField('Something fun', [validate_bio], render_kw={"placeholder": "Fun facts!"})
    profile_pic = FileField('Profile picture')


class LoginForm(FlaskForm):
	username = StringField('Username', [validators.DataRequired()], render_kw={"placeholder": "Username"})
	password = PasswordField('Password', [validators.DataRequired()], render_kw={"placeholder": "Password"})


class PostForm(FlaskForm):
    content = TextAreaField(
        '',
        validators=[validators.DataRequired(), validators.Length(max=5000)],
        render_kw={"placeholder": "Write a post..."}
    )
