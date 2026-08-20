# Anime Recommendations Web App

A Flask + MySQL web application to manage an anime list, track details, and view recommendations.

## Project Structure
- `server.py`: Flask application entry point and routes
- `db_config.py`: MySQL connection pool configuration using environment variables
- `templates/`: Jinja templates
- `static/`: CSS and image assets
- `schema.sql`: MySQL schema
- `requirements.txt`: Python dependencies
- `Procfile`: Gunicorn start command for process-based platforms
- `render.yaml`: Render deployment configuration

## Local Setup
1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`.
4. Create the MySQL database and table:

```sql
SOURCE schema.sql;
```

5. Run the app locally:

```bash
python server.py
```

The app will start on `http://127.0.0.1:5000/`.

## Required Environment Variables
- `FLASK_SECRET_KEY`
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

Optional:
- `FLASK_ENV`
- `FLASK_DEBUG`
- `DB_POOL_NAME`
- `DB_POOL_SIZE`
- `PORT`

## Production Start Command

```bash
gunicorn --bind 0.0.0.0:$PORT server:app
```

## Recommended Deployment Target
Render is a good fit for this app because it supports persistent Python web services with Gunicorn and external MySQL databases cleanly.

## Deployment Steps
1. Push this repository to GitHub.
2. Create a MySQL database with a managed provider.
3. In Render, create a new Web Service from the repo.
4. Set the build command to:

```bash
pip install -r requirements.txt
```

5. Set the start command to:

```bash
gunicorn --bind 0.0.0.0:$PORT server:app
```

6. Configure the required environment variables in the Render dashboard.
7. Run `schema.sql` against the target MySQL database before first use.

## Notes
- Do not commit `.env` or real credentials.
- `localhost` is no longer assumed for the database host.
- Flask debug mode is disabled for production execution.
