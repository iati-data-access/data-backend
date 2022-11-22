# CDFD Backend

This is the back-end to IATI's Country Development Finance Data tool.

It provides a very simple framework to access the data, based on [a modified version of the Babbage library](https://github.com/markbrough/babbage/tree/dev) that previously powered [OpenSpending](https://github.com/openspending).

It also provides a set of import scripts, based on parsing data generated from the original CDFD libraries.

## Installation

1. Set up a virtual environment and install the requirements:

```
virtualenv ./pyenv
source ./pyenv/bin/activate
pip install -r requirements.txt
```

2. Set up a database:

```
psql createdb -d iatidatacube
```

3. Adjust config file if necessary.

```
cp config.py.tmpl config.py
```

4. Install nginx and [uwsgi](https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html) - you can use and adjust the following templates:

* cdfd.nginx.conf -> nginx config file
* cdfd_uwsgi.ini -> uwsgi
* cdfd.service -> systemd service

5. Setup [certbot](https://certbot.eff.org/instructions)

## Importing data

This is still a little bit of a work in progress. CDFD Backend is currently using CSV versions of the same files which are [publicly available](https://countrydata.iatistandard.org/). The advantage of these files, compared with the XLSX files, is that they are much faster to read and parse, and that they contain codes separately from the labels, which is more convenient for storing in the database.

There are a set of commands available for downloading, parsing and storing the data. This workflow should be improved further in future.

1. Download data from [IATI Data Dump](https://iati-data-dump.codeforiati.org):

```
flask download
```

2. Process the data using the CDFD scripts - outputs data to `/output/csv/`, creating two files (transactions, and budgets) per country/region:

```
flask process-data
```

3. Setup codelists in the database:

```
flask setup-codelists
```

4. Once the data has finished being processed, you can run the following command to import all files, which are imported in alphabetical order from the `output/csv` directory:
```
flask update
```

But you might prefer to load only some files, or load files in different processes. For that, you can add `-s` for the first (starting) file you would like to process, and `-e` for the last (ending) file you would like to process. For example, to load all country transaction files, we would run:

```
flask update -s transaction-AD.csv -e transaction-ZW.csv
```

And to load all country budget files:

```
flask update -s budget-AD.csv -e budget-ZW.csv
```

5. If you want to delete everything from the database and start again, you can run:

```
flask drop-db
```
