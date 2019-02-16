INIT DJANGO PROJECT:
django-admin startproject demo_project


START DJANGO SERVER
python manage.py runserver
OR (PREFER THIS!)
python start-django.py



CREATE BASIC PAGES (LIKE HOME, ABOUT ETC..)
python manage.py startapp pages



CREATE CUSTOM USER MODEL
python manage.py startapp users

MIGRATE CREATED USER'S TO DB
python manage.py makemigrations users
python manage.py migrate users

CREATE SUPER USER
python manage.py createsuperuser