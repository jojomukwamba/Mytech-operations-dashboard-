# FTP Ops – Future Tech Professionals Operations Dashboard

A Django-based operations management system for Future Tech Professionals.  
**Module 1: Job Tracking**

---

## Quick Start (Windows)

### 1. Open a terminal in this folder

```
cd "OPERATIONS DASH BOARD"
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

The `.env` file is already pre-configured for **SQLite** (no PostgreSQL needed for local dev).  
To switch to PostgreSQL, edit `.env`:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ftpops_db
DB_USER=your_pg_user
DB_PASSWORD=your_pg_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Run migrations

```powershell
python manage.py migrate
```

### 6. Seed sample data (creates admin user + sample jobs)

```powershell
python manage.py seed_data
```

Credentials: **admin / admin123**

### 7. Start the development server

```powershell
python manage.py runserver
```

Visit: http://127.0.0.1:8000

---

## URL Map

| URL | Page |
|-----|------|
| `/` | Dashboard (Kanban + summary cards) |
| `/jobs/` | Job list with filters |
| `/jobs/new/` | Create a new job card |
| `/jobs/<id>/` | Job detail, comments, attachments, status history |
| `/jobs/<id>/edit/` | Edit a job card |
| `/engineers/workload/` | Engineer workload table |
| `/admin/` | Django admin |

---

## Project Structure

```
OPERATIONS DASH BOARD/
├── ftpops/           # Django project (settings, urls, wsgi)
├── jobs/             # Job Tracking app
│   ├── models.py     # All data models
│   ├── views.py      # All views
│   ├── forms.py      # Django forms
│   ├── admin.py      # Admin config
│   ├── signals.py    # Auto status history signal
│   ├── urls.py       # App URL patterns
│   ├── templatetags/ # Custom template filters
│   └── management/
│       └── commands/
│           └── seed_data.py
├── templates/        # HTML templates
│   ├── base.html
│   ├── registration/login.html
│   └── jobs/
│       ├── dashboard.html
│       ├── job_list.html
│       ├── job_detail.html
│       ├── job_form.html
│       └── engineer_workload.html
├── static/
│   ├── css/main.css
│   └── js/main.js
├── manage.py
├── requirements.txt
└── .env
```

---

## Adding the Next Module (Vehicle Mileage)

Create a new app alongside `jobs/`:
```powershell
python manage.py startapp vehicles
```
Add `'vehicles'` to `INSTALLED_APPS` in `ftpops/settings.py`, then wire up its URLs in `ftpops/urls.py`.

---

## Default Admin Credentials

| Username | Password |
|----------|----------|
| admin | admin123 |

⚠️ **Change the password in production.**
