# Django migration

This branch adds a Django + Django REST Framework backend alongside the working Flask application. The existing MySQL tables are mapped with `managed = False`, so Django does not create or alter the existing schema.

## Local setup

From the repository root:

```bash
python -m venv .venv-django
.venv-django\Scripts\activate
pip install -r requirements.txt
```

Set the same MySQL environment variables used by the Flask app. The Django backend reads `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME`.

Start the API:

```bash
cd django_app
python manage.py runserver
```

The API runs at `http://127.0.0.1:8000` by default.

## Postman

The API uses Basic Authentication against the existing `users` table. In Postman, select **Authorization → Basic Auth** and use the existing username/password.

### List anime

`GET /api/anime`

Optional status filter:

`GET /api/anime?status=Completed`

### Add anime

`POST /api/anime`

JSON body:

```json
{
  "title": "Attack on Titan",
  "genre": "Action",
  "status": "Watching",
  "total_episodes": 89,
  "description": ""
}
```

The API attempts to fetch the poster from Jikan with a five-second timeout. If Jikan fails, the anime is still saved with a null `poster_url`.

### Get one anime

`GET /api/anime/<anime_id>`

### Update anime

`PATCH /api/anime/<anime_id>`

### Delete anime

`DELETE /api/anime/<anime_id>`

The delete query is scoped to the authenticated user.

### Preferences

`GET /api/preferences`

`POST /api/preferences`

```json
{
  "genres": ["Action", "Fantasy"]
}
```

### Recommendations

`GET /api/recommendations`

This first migration endpoint uses the existing catalog and user preferences. Gemini integration will be moved after the CRUD API is verified.

## Important

`main` remains the working Flask version. This branch is the Django migration and should be tested with Postman before the frontend is switched over.
