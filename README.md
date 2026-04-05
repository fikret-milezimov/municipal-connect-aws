# Municipal Connect

Municipal Connect is a community-driven web platform built with Django.
It allows citizens to report local issues, share skills, and exchange items within their municipality.

The goal of the project is to improve communication between residents and make small community problems more visible and easier to solve.

---

## 🚀 Features

* Report local issues (full CRUD functionality)
* Share personal skills and services
* Marketplace for offers, requests, and giveaways
* Notification system for updates
* Role-based permissions (Moderators, ContentManagers)
* Search functionality
* Announcements section
* Background slideshow (JavaScript)
* Django messages for user feedback
* Custom error pages (404)
* REST API (Django REST Framework)
* Asynchronous tasks (Celery + Redis)

---

## 🧱 Project Structure

common         - home page, announcements, shared logic
accounts       - authentication, profiles, user logic
reports        - reporting local issues
skills         - skill sharing between users
marketplace    - marketplace items
notifications  - notification system
api            - REST API endpoints

---

## 🛠️ Tech Stack

* Python 3.12
* Django 6
* Django REST Framework
* PostgreSQL
* Docker & Docker Compose
* Nginx + Gunicorn
* Redis + Celery
* Brevo (SMTP email service)
* Bootstrap 5
* JavaScript

---

## ⚙️ Setup (Local Development)

### 1. Clone repository

git clone https://github.com/fikret-milezimov/municipal-connect-aws.git
cd municipal-connect-aws

---

### 2. Create `.env` file

Create a `.env` file based on `.env.template`:

SECRET_KEY =
DB_NAME =
DB_PASS =
DB_USER =
DB_HOST =
DB_PORT =
DEBUG =
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
EMAIL_HOST=
EMAIL_PORT=
EMAIL_USE_TLS=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
---

### 3. Run with Docker

docker-compose up --build

---

### 4. Apply migrations

docker-compose exec web python manage.py migrate

---

### 5. (Optional) Seed demo data

docker-compose exec web python manage.py seed_data

---

### 6. Access the app

http://127.0.0.1:8000/

Admin panel:
http://127.0.0.1:8000/admin/

---

## 🚀 Deployment

The project is deployed using AWS EC2 with Docker Compose.

Stack:

* Nginx (reverse proxy)
* Gunicorn (application server)
* PostgreSQL
* Redis + Celery
* AWS S3 (static/media files)
* Brevo (SMTP email service)

---

## 🔌 API

Example endpoints:

GET    /api/reports/
POST   /api/reports/
PATCH  /api/reports/{id}/

* Authentication is required for modifying data
* Permissions are based on ownership and roles

---

## 🧪 Tests

Run tests with:

python manage.py test

The project includes tests for:

* Models
* Views
* Forms
* Permissions
* API endpoints

---

## 🔐 Security

* CSRF protection enabled
* Authentication & authorization checks
* Role-based permissions
* Environment variables for sensitive data
* Protection against unauthorized object access

---

## 🎯 Purpose

This project was built as part of the Django Advanced course at SoftUni.

The goal was to design and implement a real-world application that demonstrates:

* clean architecture
* modular design
* REST API integration
* asynchronous processing
* production-ready deployment

---

## 📸 Screenshots

(Add screenshots here if available)

---

## 📌 Notes

The project follows Django best practices, using class-based views, reusable templates, and clear separation of concerns.
