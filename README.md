# Examination Management Portal (EMP)

A Flask + SQLite web app where an admin sets up exams, examiners create slots and evaluate, and students book slots and see results.

## How to run

1. `python3 -m venv venv`
2. Activate it: `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)
3. `pip install -r requirements.txt`
4. `python app.py`
5. Open http://127.0.0.1:5001 (port 5001, because macOS uses 5000 for AirPlay)

## Default admin login

Email `admin@emp.com`, password `admin123` (set in `config.py`).

## Roles

- Admin: courses, exams, rubrics, examiners, exam status, all slots and bookings, reschedule, search.
- Examiner: registers, then needs admin approval; creates slots and evaluates students.
- Student: registers and can log in straight away; books slots, cancels, sees results.

## Notes

- The database is created automatically in `instance/emp.db` on the first run.
- To reset all data, stop the app and delete `instance/emp.db`.

## Folder overview

- `app.py`: starts the app; `config.py`: settings and admin login; `requirements.txt`: packages
- `database.py`, `database_setup.py`: the db object; creates tables and the admin
- `models/`: one file per table; `rules/`: business rules; `helpers/`: small shared functions
- `routes/`: pages per role (auth, admin, examiner, student); `templates/`: HTML pages
- `static/`: local Bootstrap CSS and JS
