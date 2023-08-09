import os
SQLALCHEMY_DATABASE_URI = os.environ.get('IATI_DATA_BACKEND_DB', 'postgresql://localhost/iatidatacubetest')
SQLALCHEMY_TRACK_MODIFICATIONS = False
FLASK_ENV='development'
FLASK_DEBUG=False
BABBAGE_PAGE_MAX=1048575 # Excel maximum rows (-1 for the header)