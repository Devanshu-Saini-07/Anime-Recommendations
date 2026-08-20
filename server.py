import os
from contextlib import closing

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request

from db_config import connect


load_dotenv()

app = Flask(__name__)

is_production = os.getenv("FLASK_ENV", "production").lower() == "production"
secret_key = os.getenv("FLASK_SECRET_KEY")
if is_production and not secret_key:
    raise RuntimeError("Missing required environment variable: FLASK_SECRET_KEY")

app.config["SECRET_KEY"] = secret_key or "development-only-secret-key"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = is_production


def fetch_all(query, params=None):
    with closing(connect()) as db:
        with closing(db.cursor()) as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()


def fetch_one(query, params=None):
    with closing(connect()) as db:
        with closing(db.cursor()) as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()


def execute_query(query, params=None):
    with closing(connect()) as db:
        with closing(db.cursor()) as cursor:
            cursor.execute(query, params or ())
            db.commit()


@app.route("/")
def home():
    status = request.args.get("status")

    if status and status != "All":
        anime_list = fetch_all("SELECT * FROM anime WHERE status=%s", (status,))
    else:
        anime_list = fetch_all("SELECT * FROM anime")

    return render_template("index.html", anime_list=anime_list, selected_status=status)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        title = request.form["title"]
        genre = request.form["genre"]
        status = request.form["status"]
        total_episodes = request.form["total_episodes"]

        query = "INSERT INTO anime (title, genre, status, total_episodes) VALUES (%s, %s, %s, %s)"
        execute_query(query, (title, genre, status, total_episodes))
        return redirect("/")

    return render_template("add.html")


@app.route("/details/<int:anime_id>")
def details(anime_id):
    anime = fetch_one("SELECT * FROM anime WHERE anime_id=%s", (anime_id,))
    return render_template("details.html", anime=anime)


@app.route("/recommendations")
def recommendations():
    recommendations = fetch_all("SELECT * FROM anime WHERE status='Completed'")
    return render_template("recommendations.html", recommendations=recommendations)


@app.route("/edit/<int:anime_id>", methods=["GET", "POST"])
def edit(anime_id):
    if request.method == "POST":
        title = request.form["title"]
        genre = request.form["genre"]
        status = request.form["status"]
        total_episodes = request.form["total_episodes"]

        execute_query(
            """
            UPDATE anime
            SET title=%s, genre=%s, status=%s, total_episodes=%s
            WHERE anime_id=%s
            """,
            (title, genre, status, total_episodes, anime_id),
        )
        return redirect("/")

    anime = fetch_one("SELECT * FROM anime WHERE anime_id=%s", (anime_id,))
    return render_template("edit.html", anime=anime)


@app.route("/delete/<int:anime_id>", methods=["POST"])
def delete(anime_id):
    execute_query("DELETE FROM anime WHERE anime_id=%s", (anime_id,))
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
