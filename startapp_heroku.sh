export ARBEITSZEIT_APP_CONFIGURATION="$PWD/production-settings.py"

echo "Compiling translation files..."
pybabel compile -d arbeitszeit_flask/translations

gunicorn wsgi:app
