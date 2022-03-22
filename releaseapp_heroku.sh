export FLASK_APP=arbeitszeit_flask
export ARBEITSZEIT_APP_CONFIGURATION="$PWD/arbeitszeit_flask/production_settings.py"
flask db upgrade
