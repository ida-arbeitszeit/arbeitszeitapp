#!/bin/bash
# to be excuted from root folder

# create list of python-files that get translated
python ./translations/create_files_to_translate.py

# create .po-files (for every locale; joins with existing files)
DOMAIN=arbeitszeitapp
LOCALES="es_ES de_DE"
for locale in $LOCALES
do
    touch ./translations/$locale/LC_MESSAGES/$DOMAIN.po
    xgettext --from-code utf-8 -f ./translations/files_to_translate.txt -o ./translations/$locale/LC_MESSAGES/$DOMAIN.po -j
done

# create .mo-files from recently created .po-files
for locale in $LOCALES
do
    msgfmt ./translations/$locale/LC_MESSAGES/$DOMAIN.po -o ./translations/$locale/LC_MESSAGES/$DOMAIN.mo
done
