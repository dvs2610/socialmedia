import bcrypt
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, redirect, render_template, url_for, session
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import Base, User

# As of now public for first try, change to actual secret variable or os.environ.get
app = Flask(__name__)
app.config["SECRET_KEY"]="43A2E58F63F24669186D7A8F8B6DF5593C3FF11B53E4FBDA13691AB98441E85AEB32479C3365E6144A3AE72"
engine = create_engine("sqlite:///socialmedia.db", echo=True)
SEED_USERS_FILE = Path(__file__).with_name("seed_users.json")

def initialize_database():
	Base.metadata.create_all(engine)

	with SEED_USERS_FILE.open(encoding="utf-8") as seed_file:
		seed_users = json.load(seed_file)

	with Session(engine) as db:
		existing_usernames = set(db.scalars(select(User.username)).all())
		for seed_user in seed_users:
			seed_birthday = datetime.fromisoformat(seed_user["birthday"])
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

@app.route('/', methods=['GET', 'POST'])
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if not session.get("name"):
		session["name"] = "logged_in_user_hi"
	return redirect(url_for("index"))

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
	app.run(debug=True)