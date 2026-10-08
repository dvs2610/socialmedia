Social Media Platform

Ultimate goal:
* Create account
* Follow other accounts and become friends
* Post and view content


Create virtual environment, install Flask and run app

* py -3 -m venv .venv
* .venv\Scripts\activate
* pip install -r requirements.txt
* python -m flask
* python -m flask --app app run --debug

The first time the app starts, it creates `socialmedia.db` and loads the example users and posts from `seed_users.json` and `seed_posts.json`. Existing users and posts are left unchanged, so the seed process is safe to run every time the app starts. The example users all use `password` until login functionality is implemented.