# Anime Recommendations / Anime Tracker

A simple Flask and MySQL web app for tracking anime you want to watch, are currently watching, or have already completed. The project includes basic CRUD functionality, a recommendations view, local test coverage for core routes, and a live deployment on Render.

## Live Demo

https://anime-recommendations-r9zx.onrender.com/

## Features

- View your anime list on the home page
- Add a new anime entry with title, genre, status, and total episodes
- Open a details page for a specific anime
- Edit existing anime entries
- Delete anime entries
- Filter the list by watch status
- View completed anime in a separate recommendations page

## Tech Stack

- Python
- Flask
- MySQL
- mysql-connector-python
- Gunicorn
- HTML templates with Jinja
- CSS
- Render for deployment
- Aiven for managed MySQL hosting

## Project Structure

- `server.py` - Main Flask app and route logic
- `db_config.py` - MySQL connection pool setup using environment variables
- `schema.sql` - Database schema for the `anime` table
- `templates/` - HTML templates for list, add, edit, details, and recommendations pages
- `static/` - Static assets such as CSS and images
- `tests/test_routes.py` - Basic route tests using mocked database connections
- `requirements.txt` - Python dependencies
- `Procfile` - Gunicorn start command
- `render.yaml` - Render deployment configuration
- `.env.example` - Example local environment configuration

## How to Run Locally

1. Clone the repository.

```bash
git clone <https://github.com/Devanshu-Saini-07/Anime-Recommendations.git>
cd "Anime Recommendations"
```

2. Create and activate a virtual environment.

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

3. Install the required packages.

```bash
pip install -r requirements.txt
```

4. Create a `.env` file using `.env.example` as a guide.

5. Create your MySQL database, then run the schema in `schema.sql`.

Example:

```sql
SOURCE schema.sql;
```

6. Start the Flask app.

```bash
python server.py
```

7. Open the app in your browser:

```text
http://127.0.0.1:5000/
```

## Environment Variables

The app reads configuration from environment variables.

Required:

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

Example `.env` values:

```env
FLASK_ENV=production
FLASK_DEBUG=0
FLASK_SECRET_KEY=replace-with-a-long-random-secret

DB_HOST=your-mysql-host
DB_PORT=3306
DB_USER=your-mysql-user
DB_PASSWORD=your-mysql-password
DB_NAME=anime_tracker

DB_POOL_NAME=anime_pool
DB_POOL_SIZE=5
```

## Database

This project uses MySQL for storing anime entries. In production, it is configured to connect to an external managed MySQL database such as Aiven. The Flask app uses `mysql-connector-python` with a small connection pool defined in `db_config.py`.

The main table used by the app is:

- `anime`

## Using the Deployed App

1. Open the live app:
   `https://anime-recommendations-r9zx.onrender.com/`
2. Browse the anime list on the home page
3. Add a new anime entry from the add page
4. Edit or delete entries as needed
5. Open the recommendations page to view completed anime

## Deployment Note

When deploying to Render on Linux, MySQL table names are case-sensitive. This project was updated to use a consistent lowercase table name:

- `anime`

This matters because queries using `Anime` can fail on Linux even if they worked on a case-insensitive local setup.

## Testing

Run the included route tests with:

```bash
python -m unittest tests.test_routes
```

## Notes

- Keep `.env` and real database credentials out of version control
- Use `schema.sql` to initialize the required table before first run
- Render uses Gunicorn to run the production app
