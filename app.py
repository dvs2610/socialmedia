import bcrypt
import json
import secrets
from pathlib import Path
from datetime import date, datetime
from flask import Flask, flash, redirect, render_template, url_for, session, request
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import Base, User
from wtforms import DateField, StringField, PasswordField, validators
from flask_wtf import FlaskForm

app = Flask(__name__)
SECRET_KEY_FILE = Path(__file__).with_name("secret_key.txt")
if not SECRET_KEY_FILE.exists():
	SECRET_KEY_FILE.write_text(secrets.token_hex(32), encoding="utf-8")
app.config["SECRET_KEY"] = SECRET_KEY_FILE.read_text(encoding="utf-8").strip()
engine = create_engine("sqlite:///socialmedia.db", echo=True)

SEED_USERS_FILE = Path(__file__).with_name("seed_users.json")

def initialize_database():
	Base.metadata.create_all(engine)

	with SEED_USERS_FILE.open(encoding="utf-8") as seed_file:
		seed_users = json.load(seed_file)

	with Session(engine) as db:
		existing_usernames = set(db.scalars(select(User.username)).all())
		for seed_user in seed_users:
			seed_birthday = date.fromisoformat(seed_user["birthday"])
			if seed_user["username"] in existing_usernames:
				continue

			db.add(User(
				username=seed_user["username"],
				password_hash=bcrypt.hashpw(
					seed_user["password"].encode("utf-8"),
					bcrypt.gensalt()
				).decode("utf-8"),
					birthday=seed_birthday,
				fullname=seed_user.get("fullname"),
				location=seed_user.get("location"),
				something_fun=seed_user.get("something_fun"),
			))
			db.commit()

initialize_database()

@app.before_request
def check_logged_in():
	# prevent endless loop from login page itself and exception for static (css) and register
	if request.endpoint in {"login", "static", "register"}:
		return None
	
	if not session.get("name"):
		return redirect(url_for('login'))

@app.context_processor
def current_user():
	return {
		"current_user": session.get("name") or None
	}

@app.context_processor
def all_users():
	with Session(engine) as db:
		return {
			"all_users": db.scalars(select(User)).all()
		}

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=10)])
    password = PasswordField('Password', [
		validators.Length(min=8, max=32),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords don\'t match.')
    ])
    confirm = PasswordField('Confirm Password')
    birthday = DateField('Birthday')
    fullname = StringField('Full name', [validators.Length(max=60)])
    location = StringField('Location', [validators.Length(max=80)])
    bio = StringField('Something fun', [validators.Length(max=120)])

@app.route('/', methods=['GET', 'POST'])
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if session.get("name"):
		return redirect(url_for("index"))
	if request.method == "POST":
		username = request.form.get("username", "")
		password = request.form.get("password", "")
		with Session(engine) as db:
			user = db.scalar(select(User).where(User.username == username))
		if user and bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
			session["name"] = user.username
			return redirect(url_for("index"))
		flash("The username and password combination is incorrect.", "error")
	return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()

	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		birthday = form.birthday.data
		fullname = form.fullname.data
		location = form.location.data
		bio = form.bio.data

		with Session(engine) as db:
			if db.scalar(select(User).where(User.username == username)):
				form.username.errors.append("That username is already taken.")
				return render_template('register.html', form=form)

			db.add(User(
				username=username,
				password_hash=bcrypt.hashpw(
					password.encode("utf-8"),
					bcrypt.gensalt()
				).decode("utf-8"),
				birthday=birthday or None,
				fullname=fullname or None,
				location=location or None,
				something_fun=bio or None,
			))
			db.commit()
		return redirect(url_for("index"))
	return render_template('register.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
	if session.get("name"):
		session["name"] = None
	return redirect(url_for("index"))

@app.route('/<username>', methods=['GET', 'POST'])
def profile(username):
	with Session(engine) as db:
		user = db.scalar(select(User).where(User.username == username))
	return render_template('profile.html', username=username, user=user)

if __name__ == '__main__':
	app.run()
