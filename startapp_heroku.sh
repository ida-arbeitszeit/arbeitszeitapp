export ARBEITSZEIT_APP_CONFIGURATION="$PWD/production-settings.py"
gunicorn wsgi:app
