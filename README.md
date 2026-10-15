Social Media Platform

Languages and frameworks: 
* Python
* Flask/Jinja
* SQLAlchemy
* HTML+CSS

On this app, users can:
* Create an account
* Write a post
* View other posts and users

In future versions, this might be elaborated with:
* Following other accounts
* Liking and commenting on posts
* Search options/filters for users

Create virtual environment, install requirements and run app:
* cd socialmedia
* py -3 -m venv .venv
* .venv\Scripts\activate
* pip install -r requirements.txt
* python -m flask
* python -m flask --app app run --debug

The first time the app starts, it creates `socialmedia.db` and loads the example users and posts from `seed_users.json` and `seed_posts.json`. Existing users and posts are left unchanged, so the seed process is safe to run every time the app starts. The example users all use `password` as password.
