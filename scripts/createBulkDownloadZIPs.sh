#!/usr/bin/bash

if [ ! -d ".git" ]; then
    echo "$0: script must be run from the root of the CDFD backend repository"
    exit 1
fi

git remote -v | grep "iati-data-access/data-backend.git" > /dev/null

if [ "$?" != 0 ]; then
    echo "$0: script must be run from the root of the CDFD backend repository"
    exit 1
fi

if [ ! -d "output/web/xlsx" ]; then
    echo "$0: Excel files have not yet been generated; skipping creation of ZIP files"
    exit 2
fi

cd output/web/xlsx

for LANG in 'en' 'fr' 'es' 'pt';
do
    zip -r tmp-cdfd-xlsx-files-$LANG.zip $LANG
    mv tmp-cdfd-xlsx-files-$LANG.zip cdfd-xlsx-files-$LANG.zip
done

cd ../../..
