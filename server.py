import os
from contextlib import closing
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from db_config import connect


load_dotenv()

app = Flask(__name__)

flask_env = os.getenv("FLASK_ENV", "").strip().lower()
render_external_url = os.getenv("RENDER_EXTERNAL_URL", "").strip().lower()
is_render = os.getenv("RENDER", "").strip().lower() == "true"
is_production = (
    flask_env == "production"
    or is_render
    or render_external_url.startswith("https://")
)
secret_key = os.getenv("FLASK_SECRET_KEY")
if is_production and not secret_key:
    raise RuntimeError("Missing required environment variable: FLASK_SECRET_KEY")

app.config["SECRET_KEY"] = secret_key or "development-only-secret-key"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = is_production
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"
app.config["REMEMBER_COOKIE_SECURE"] = is_production

STATUS_OPTIONS = ("All", "Watching", "Completed", "Plan to Watch")
ONBOARDING_GENRES = (
    "Action",
    "Adventure",
    "Comedy",
    "Romance",
    "Fantasy",
    "Dark Fantasy",
    "Horror",
    "Thriller",
    "Mystery",
    "Sci-Fi",
    "Sports",
    "Supernatural",
    "Drama",
    "Slice of Life",
    "Psychological",
)
DEFAULT_ANIME_DESCRIPTION = (
    "A standout entry in your anime journey with unforgettable character arcs, atmosphere, "
    "and story beats worth revisiting."
)


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
            return getattr(cursor, "lastrowid", None)


def sanitize_total_episodes(raw_value):
    try:
        total = int(raw_value)
    except (TypeError, ValueError):
        return 0
    return max(total, 0)


def dict_from_anime_row(row):
    if not row:
        return None

    return {
        "anime_id": row[0],
        "title": row[1],
        "genre": row[2] or "Unknown Genre",
        "status": row[3] or "Plan to Watch",
        "total_episodes": row[4] or 0,
        "description": row[5] or DEFAULT_ANIME_DESCRIPTION,
        "poster_hint": row[6] or (row[2] or "Anime"),
        "user_id": row[7] if len(row) > 7 else None,
    }


def dict_list(rows):
    return [dict_from_anime_row(row) for row in rows]


def get_status_counts(user_id):
    counts = {"All": 0, "Watching": 0, "Completed": 0, "Plan to Watch": 0}
    rows = fetch_all(
        "SELECT status, COUNT(*) FROM anime WHERE user_id=%s GROUP BY status",
        (user_id,),
    )

    total = 0
    for status, count in rows:
        if status in counts:
            counts[status] = count
            total += count

    counts["All"] = total
    return counts


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None

    row = fetch_one(
        """
        SELECT user_id, username, email, preferences_completed_at
        FROM users
        WHERE user_id=%s
        """,
        (user_id,),
    )
    if not row:
        session.clear()
        return None

    return {
        "user_id": row[0],
        "username": row[1],
        "email": row[2],
        "has_completed_preferences": row[3] is not None,
    }


def get_user_preferences(user_id):
    rows = fetch_all(
        """
        SELECT genre_name
        FROM user_preferences
        WHERE user_id=%s
        ORDER BY genre_name ASC
        """,
        (user_id,),
    )
    return [row[0] for row in rows]


def get_preference_summary(user_id):
    preferences = get_user_preferences(user_id)
    return {
        "genres": preferences,
        "count": len(preferences),
        "completed": bool(preferences),
    }


def get_user_watch_history(user_id):
    rows = fetch_all(
        """
        SELECT anime_id, title, genre, status, total_episodes, description, poster_hint, user_id
        FROM anime
        WHERE user_id=%s
        ORDER BY anime_id DESC
        """,
        (user_id,),
    )
    return dict_list(rows)


def get_recommendation_candidates(user_id):
    preferences = get_user_preferences(user_id)
    excluded_titles = fetch_all(
        """
        SELECT DISTINCT title
        FROM anime
        WHERE user_id=%s AND status IN ('Watching', 'Completed', 'Plan to Watch')
        """,
        (user_id,),
    )
    excluded_titles = {row[0].strip().lower() for row in excluded_titles if row and row[0]}

    if preferences:
        placeholders = ", ".join(["%s"] * len(preferences))
        query = f"""
            SELECT anime_id, title, genre, status, total_episodes, description, poster_hint, user_id
            FROM anime
            WHERE user_id <> %s
              AND genre IN ({placeholders})
            ORDER BY anime_id DESC
            LIMIT 24
        """
        rows = fetch_all(query, (user_id, *preferences))
    else:
        rows = fetch_all(
            """
            SELECT anime_id, title, genre, status, total_episodes, description, poster_hint, user_id
            FROM anime
            WHERE user_id <> %s
            ORDER BY anime_id DESC
            LIMIT 24
            """,
            (user_id,),
        )

    candidates = []
    seen_titles = set()
    for anime in dict_list(rows):
        normalized_title = anime["title"].strip().lower()
        if normalized_title in excluded_titles or normalized_title in seen_titles:
            continue
        seen_titles.add(normalized_title)
        candidates.append(anime)
    return candidates


def get_dashboard_sections(user_id):
    watch_history = get_user_watch_history(user_id)
    grouped = {status: [] for status in STATUS_OPTIONS if status != "All"}
    for anime in watch_history:
        grouped.setdefault(anime["status"], []).append(anime)
    return grouped


def get_user_anime(anime_id, user_id):
    return dict_from_anime_row(
        fetch_one(
            """
            SELECT anime_id, title, genre, status, total_episodes, description, poster_hint, user_id
            FROM anime
            WHERE anime_id=%s AND user_id=%s
            """,
            (anime_id, user_id),
        )
    )


def save_user_preferences(user_id, genres):
    unique_genres = [genre for genre in ONBOARDING_GENRES if genre in genres]
    execute_query("DELETE FROM user_preferences WHERE user_id=%s", (user_id,))
    for genre in unique_genres:
        execute_query(
            "INSERT INTO user_preferences (user_id, genre_name) VALUES (%s, %s)",
            (user_id, genre),
        )

    execute_query(
        """
        UPDATE users
        SET preferences_completed_at=COALESCE(preferences_completed_at, CURRENT_TIMESTAMP)
        WHERE user_id=%s
        """,
        (user_id,),
    )


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not g.user:
            flash("Please log in to continue your anime journey.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


def redirect_authenticated_user():
    if g.user:
        return redirect(url_for("home"))
    return None


def normalize_next_url():
    next_url = request.args.get("next") or request.form.get("next")
    if next_url and next_url.startswith("/"):
        return next_url
    return url_for("home")


@app.before_request
def load_logged_in_user():
    g.user = get_current_user()


@app.context_processor
def inject_globals():
    return {
        "status_options": STATUS_OPTIONS,
        "current_user": g.user,
        "is_authenticated": g.user is not None,
        "genre_options": ONBOARDING_GENRES,
    }


@app.route("/")
@login_required
def home():
    if not g.user["has_completed_preferences"]:
        return redirect(url_for("preferences"))

    status = request.args.get("status", "All")
    user_id = g.user["user_id"]

    if status not in STATUS_OPTIONS:
        status = "All"

    watch_history = get_user_watch_history(user_id)
    if status == "All":
        filtered_anime = watch_history
    else:
        filtered_anime = [anime for anime in watch_history if anime["status"] == status]

    return render_template(
        "index.html",
        anime_list=filtered_anime,
        selected_status=status,
        status_counts=get_status_counts(user_id),
        preference_summary=get_preference_summary(user_id),
        dashboard_sections=get_dashboard_sections(user_id),
        recommendation_candidates=get_recommendation_candidates(user_id)[:6],
    )


@app.route("/signup", methods=["GET", "POST"])
def signup():
    redirect_response = redirect_authenticated_user()
    if redirect_response:
        return redirect_response

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("Username, email, and password are required.", "error")
        elif password != confirm_password:
            flash("Passwords do not match.", "error")
        elif len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
        elif fetch_one(
            "SELECT user_id FROM users WHERE username=%s OR email=%s",
            (username, email),
        ):
            flash("That username or email is already in use.", "error")
        else:
            user_id = execute_query(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, generate_password_hash(password)),
            )
            session.clear()
            session["user_id"] = user_id
            flash("Your account is ready. Welcome aboard.", "success")
            return redirect(url_for("preferences"))

    return render_template("signup.html", next_url=normalize_next_url())


@app.route("/login", methods=["GET", "POST"])
def login():
    redirect_response = redirect_authenticated_user()
    if redirect_response:
        return redirect_response

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        remember_me = request.form.get("remember_me") == "on"

        user = fetch_one(
            """
            SELECT user_id, username, email, password_hash, preferences_completed_at
            FROM users
            WHERE email=%s OR username=%s
            """,
            (identifier.lower(), identifier),
        )

        if not user or not check_password_hash(user[3], password):
            flash("Invalid username/email or password.", "error")
        else:
            session.clear()
            session["user_id"] = user[0]
            session.permanent = remember_me
            flash(f"Welcome back, {user[1]}.", "success")
            destination = "home" if user[4] else "preferences"
            return redirect(url_for(destination))

    return render_template("login.html", next_url=normalize_next_url())


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/preferences", methods=["GET", "POST"])
@login_required
def preferences():
    current_preferences = get_user_preferences(g.user["user_id"])

    if request.method == "POST":
        selected_genres = request.form.getlist("genres")
        valid_genres = [genre for genre in selected_genres if genre in ONBOARDING_GENRES]

        if not valid_genres:
            flash("Choose at least one genre to personalize your dashboard.", "error")
        else:
            save_user_preferences(g.user["user_id"], valid_genres)
            g.user["has_completed_preferences"] = True
            flash("Your anime preferences are saved.", "success")
            return redirect(url_for("home"))

    return render_template(
        "preferences.html",
        selected_genres=current_preferences,
        is_edit_mode=g.user["has_completed_preferences"],
    )


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if not g.user["has_completed_preferences"]:
        return redirect(url_for("preferences"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        genre = request.form.get("genre", "").strip()
        status = request.form.get("status", "Watching")
        total_episodes = sanitize_total_episodes(request.form.get("total_episodes"))
        description = request.form.get("description", "").strip()
        poster_hint = request.form.get("poster_hint", "").strip()

        if not title:
            flash("Title is required.", "error")
        elif status not in STATUS_OPTIONS:
            flash("Select a valid watch status.", "error")
        else:
            execute_query(
                """
                INSERT INTO anime (title, genre, status, total_episodes, description, poster_hint, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    title,
                    genre,
                    status,
                    total_episodes,
                    description or DEFAULT_ANIME_DESCRIPTION,
                    poster_hint or genre or title,
                    g.user["user_id"],
                ),
            )
            flash(f"{title} was added to your list.", "success")
            return redirect(url_for("home"))

    return render_template("add.html", form_mode="add", anime=None)


@app.route("/details/<int:anime_id>")
@login_required
def details(anime_id):
    anime = get_user_anime(anime_id, g.user["user_id"])
    if not anime:
        flash("We couldn't find that anime in your collection.", "error")
        return redirect(url_for("home"))

    progress_value = 100 if anime["status"] == "Completed" else 65 if anime["status"] == "Watching" else 20
    return render_template("details.html", anime=anime, progress_value=progress_value)


@app.route("/recommendations")
@login_required
def recommendations():
    candidates = get_recommendation_candidates(g.user["user_id"])
    return render_template(
        "recommendations.html",
        recommendations=candidates[:12],
        candidate_count=len(candidates),
        preference_summary=get_preference_summary(g.user["user_id"]),
    )


@app.route("/edit/<int:anime_id>", methods=["GET", "POST"])
@login_required
def edit(anime_id):
    anime = get_user_anime(anime_id, g.user["user_id"])
    if not anime:
        flash("We couldn't find that anime in your collection.", "error")
        return redirect(url_for("home"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        genre = request.form.get("genre", "").strip()
        status = request.form.get("status", "Watching")
        total_episodes = sanitize_total_episodes(request.form.get("total_episodes"))
        description = request.form.get("description", "").strip()
        poster_hint = request.form.get("poster_hint", "").strip()

        if not title:
            flash("Title is required.", "error")
        elif status not in STATUS_OPTIONS:
            flash("Select a valid watch status.", "error")
        else:
            execute_query(
                """
                UPDATE anime
                SET title=%s, genre=%s, status=%s, total_episodes=%s, description=%s, poster_hint=%s
                WHERE anime_id=%s AND user_id=%s
                """,
                (
                    title,
                    genre,
                    status,
                    total_episodes,
                    description or DEFAULT_ANIME_DESCRIPTION,
                    poster_hint or genre or title,
                    anime_id,
                    g.user["user_id"],
                ),
            )
            flash(f"{title} was updated.", "success")
            return redirect(url_for("details", anime_id=anime_id))

    return render_template("edit.html", form_mode="edit", anime=anime)


@app.route("/delete/<int:anime_id>", methods=["POST"])
@login_required
def delete(anime_id):
    anime = get_user_anime(anime_id, g.user["user_id"])
    if not anime:
        flash("That anime is no longer available.", "error")
        return redirect(url_for("home"))

    execute_query(
        "DELETE FROM anime WHERE anime_id=%s AND user_id=%s",
        (anime_id, g.user["user_id"]),
    )
    flash(f"{anime['title']} was removed from your list.", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
