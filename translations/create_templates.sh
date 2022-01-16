#!/bin/bash
# to be excuted from root folder
# creates .pot and .po files 

TRANS_DOMAIN=arbeitszeitapp
TRANS_LOCALES="es_ES de_DE"

# create list of python-files that get translated
python ./translations/create_files_to_translate.py

# create language-agnostic .pot-file
xgettext --from-code utf-8 -f ./translations/files_to_translate.txt -o ./translations/$TRANS_DOMAIN.pot

# create for each locale language-specific .po-file from .pot-file if it does not exists. 
# If exists, merge with existing file
for locale in $TRANS_LOCALES
do
    FILE=./translations/$locale/LC_MESSAGES/$TRANS_DOMAIN.po
    if [ -f "$FILE" ]
    then msgmerge "$FILE" ./translations/$TRANS_DOMAIN.pot -U
    else msginit -i ./translations/$TRANS_DOMAIN.pot -o "$FILE" --no-translator --locale=$locale.UTF-8
    fi
done

# create .mo-files from recently created .po-files
for locale in $TRANS_LOCALES
do
    msgfmt ./translations/$locale/LC_MESSAGES/$TRANS_DOMAIN.po -o ./translations/$locale/LC_MESSAGES/$TRANS_DOMAIN.mo
done
