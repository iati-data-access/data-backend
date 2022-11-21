import sys, os
PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, '/var/www/cdfd/backend/pyenv/lib/python3.8/site-packages')
sys.path.insert(0, PATH)

from wsgi import create_app
application = create_app()