#!/bin/sh

# python manage.py migrate --no-input
# python manage.py collectstatic --no-input

# DJANGO_SUPERUSER_PASSWORD=$SUPER_USER_PASSWORD python manage.py createsuperuser --username $SUPER_USER_NAME --email $SUPER_USER_EMAIL --noinput

# python3 manage.py makemigrations
# python manage.py migrate

python manage.py createsuperuser \
        --noinput \
        --username admin \
        --email andr.makar9061@yandex.ru
gunicorn cy_backend.wsgi:application --bind 0.0.0.0:8000

