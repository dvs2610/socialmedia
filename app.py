import bcrypt
import json
import secrets
from forms import RegistrationForm, LoginForm, PostForm
from pathlib import Path
from datetime import date, datetime
from flask import Flask, abort, redirect, render_template, url_for, session, request
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import Base, Post, User
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
SECRET_KEY_FILE = Path(__file__).with_name("secret_key.txt")
if not SECRET_KEY_FILE.exists():
	SECRET_KEY_FILE.write_text(secrets.token_hex(32), encoding="utf-8")
app.config["SECRET_KEY"] = SECRET_KEY_FILE.read_text(encoding="utf-8").strip()
CSRFProtect(app)
engine = create_engine("sqlite:///socialmedia.db", echo=True)


SEED_USERS_FILE = Path(__file__).with_name("seed_users.json")
SEED_POSTS_FILE = Path(__file__).with_name("seed_posts.json")


def initialize_database():
	"""Sets up database, loads users and posts, creates seed users and posts if not yet existing."""
	Base.metadata.create_all(engine)

	with SEED_USERS_FILE.open(encoding="utf-8") as seed_file:
		seed_users = json.load(seed_file)

	with SEED_POSTS_FILE.open(encoding="utf-8") as seed_file:
		seed_posts = json.load(seed_file)

	with Session(engine) as db:
		existing_usernames = set(db.scalars(select(User.username)).all())
		existing_post_ids = set(db.scalars(select(Post.id)).all())
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

		for seed_post in seed_posts:
			if seed_post["id"] in existing_post_ids:
				continue

			db.add(Post(
				id=seed_post["id"],
				author_username=seed_post["author_username"],
				content=seed_post["content"],
				created_at=datetime.fromisoformat(seed_post["created_at"]),
			))
			
		db.commit()


initialize_database()


@app.before_request
def check_logged_in():
	"""Checks before every page request if there is a user is currently logged in. If not, redirects to login page"""
	
	# Prevent endless loop from login page to itself and exceptions for static (css) and register/create account page.
	if request.endpoint in {"login", "static", "register"}:
		return None
	
	if not session.get("name"):
		return redirect(url_for('login'))


@app.context_processor
def current_user():
	# Used in profile.html
	return {
		"current_user": session.get("name") or None
	}


@app.route('/', methods=['GET', 'POST'])
def index():
	with Session(engine) as db:
		posts = db.scalars(
			select(Post)
			.order_by(Post.created_at.desc())
		).all()
	return render_template('index.html', posts=posts)


@app.route('/users', methods=['GET', 'POST'])
def users():
	with Session(engine) as db:
		users = db.scalars(select(User)).all()
	return render_template('users.html', users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if session.get("name"):
		return redirect(url_for("index"))
	
	form = LoginForm()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		with Session(engine) as db:
			user = db.scalar(select(User).where(User.username == username))
		if user and bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
			session["name"] = user.username
			return redirect(url_for("index"))
		form.password.errors.append("Invalid username or password.")
		
	return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		username = form.username.data
		password_hash = bcrypt.hashpw(
    		form.password.data.encode("utf-8"),
    		bcrypt.gensalt()
		).decode("utf-8")
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
				password_hash=password_hash,
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


@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
	with Session(engine) as db:
		post = db.get(Post, post_id)
		if post is None:
			abort(404)
		if post.author_username != session["name"]:
			abort(403)
		username = post.author_username
		db.delete(post)
		db.commit()

	# if user was on home page when deleting a post, redirects back to index. Otherwise redirects to profile page.
	if request.form.get("return_to") == "index":
		return redirect(url_for("index"))
	return redirect(url_for("profile", username=username))


@app.route('/<username>', methods=['GET', 'POST'])
def profile(username):
	with Session(engine) as db:
		user = db.scalar(select(User).where(User.username == username))
		posts = db.scalars(
			select(Post)
			.where(Post.author_username == username)
			.order_by(Post.created_at.desc())
		).all()

	form = PostForm()
	if form.validate_on_submit():
		with Session(engine) as db:
			db.add(Post(
				content=form.content.data,
				author_username=session["name"],
				created_at=datetime.now()
			))
			db.commit()
		return redirect(url_for("profile", username=username))
	return render_template('profile.html', username=username, user=user, posts=posts, form=form)


if __name__ == '__main__':
	app.run()
