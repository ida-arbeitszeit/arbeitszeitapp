export ARBEITSZEIT_APP_CONFIGURATION="$PWD/production-settings.py"
flask db upgrade
echo "Compiling translations..."
pybabel compile -d arbeitszeit_flask/translations