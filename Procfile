web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py seed_projects && gunicorn orchestrix.wsgi --log-file -
