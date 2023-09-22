python manage.py migrate --noinput
python manage.py collectstatic --noinput
cp -r ./collected_static /backend_static
gunicorn --reload  foodgram.wsgi:aplication --bind 0.0.0.8000 --access-logfile '-' --error-logfile -
exec "$@"