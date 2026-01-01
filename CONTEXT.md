# Project: Production Report Generator

## Objective
The main goal is to create a web application using Django to generate production reports. The data for there reports will be stored and retrieved from a Supabase PostgreSQL database. The application should be professional, scalable, and eventually ready for development on AWS.

## Technology Stack
- **Backend:** Django
- **Database:** Supabase (PostgreSQL)
- **Environment Management:** Python Virtual Enviroment (` .venv `)
- **Dependencies:**
  - `django`
  - `python-dotenv`
  - `dj-database-url`
  - `psycopg2-binary`
  - `supabase`
  - `bootstrap`

## Current Status
- The Django project structure has been created.
- A virtual environment ( `.venv` ) is set up and active.
- The ` .env ` file is configured with Supabase credenctials (`DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_KEY`).
- The Django  ``settings.py`` file has been modified to connect to the Supabase database using `dj-database-url`.
- The initial database migration (`python `manage.py` migrate`) has been run successfully, creating Django's default tables in the `public` schema of the Supabase database.
- An initial admin user has been created using `python`manage.py` createsuperuser`.

## Next Steps
The next logical step is to start creating the Django models that will define the structure of th production report data.

