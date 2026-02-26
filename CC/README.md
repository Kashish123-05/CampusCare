# CampusCare – Smart Campus Issue Reporting & Tracking System

A full-stack Django web application for educational institutions to report, manage, and track campus maintenance issues, with an integrated AI assistant chatbot.

## Features

- **User roles**: Student, Admin, Maintenance Staff
- **Issue management**: Submit, assign, track, resolve
- **Role-based dashboards** with analytics
- **Email notifications** on issue submission, assignment, status change, resolution
- **AI chatbot** (rule-based + optional OpenAI)
- **Real-time notification bell** (AJAX polling)
- **Export reports** to CSV

## Quick Start

### 1. Create virtual environment and install dependencies

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

### 2. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create superuser (admin)

```bash
python manage.py createsuperuser
```

Superusers automatically get the Admin role. To create maintenance staff or students, register via the website or use Django admin.

### 4. Load sample FAQs (optional)

```bash
python manage.py load_faqs
```

### 5. Run server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Project Structure

```
campuscare/
├── accounts/       # Auth, roles, profiles, signals
├── issues/         # Issue CRUD, email notifications
├── dashboard/      # Dashboards, analytics, export
├── chatbot/        # AI assistant, FAQ
├── templates/      # HTML templates
├── static/         # CSS, JS
├── media/          # Uploaded images
└── campuscare/     # Project settings
```

## Configuration

Copy `.env.example` to `.env` and set:

- `SECRET_KEY` – Django secret
- `EMAIL_*` – For email notifications (console backend used by default)
- `OPENAI_API_KEY` – For AI chatbot (optional)
- `CHATBOT_USE_OPENAI=True` – Enable OpenAI (optional)

## Usage

1. **Students**: Register → Submit issues → Track status
2. **Admin**: View all issues, assign to maintenance, analytics, export CSV
3. **Maintenance**: View assigned issues, update status, add resolution notes

## License

MIT
