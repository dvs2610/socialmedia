from flask import Flask, redirect, render_template, url_for, session

app = Flask(__name__)

# As of now public for first try, change to actual secret variable or os.environ.get
app.config["SECRET_KEY"]="43A2E58F63F24669186D7A8F8B6DF5593C3FF11B53E4FBDA13691AB98441E85AEB32479C3365E6144A3AE72"

@app.context_processor
def current_user():
	return {
		"current_user": session.get("name") or None
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
	return render_template('profile.html', username=username)

if __name__ == '__main__':
	app.run(debug=True)