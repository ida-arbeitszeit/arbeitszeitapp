export FLASK_APP=arbeitszeit_flask
export ARBEITSZEITAPP_CONFIGURATION_PATH="$PWD/arbeitszeit_flask/production_settings.py"

echo "Compiling translation files..."
python setup.py compile_catalog

gunicorn arbeitszeit_flask.wsgi:app
