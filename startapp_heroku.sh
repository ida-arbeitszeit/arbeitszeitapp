export FLASK_APP=arbeitszeit_flask
export ARBEITSZEIT_APP_CONFIGURATION="$PWD/arbeitszeit_flask/production_settings.py"

echo "Compiling translation files..."
pybabel compile -d arbeitszeit_flask/translations

gunicorn arbeitszeit_flask.wsgi:app
