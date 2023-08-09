import os
import json
import csv

from flask import url_for
import pytest

from iatidatacube.app import create_app
from iatidatacube import models
from iatidatacube.extensions import db
from iatidatacube import import_codelists

basedir = os.path.abspath(os.path.dirname(__file__))

@pytest.fixture(scope="session")
def app():
    """Session-wide test `Flask` application."""

    app = create_app('tests.config')
    app.testing = True

    with app.app_context() as client:
        db.app = app
        db.create_all()
        yield app
        db.session.close()
        db.session.remove()
        db.drop_all()


# Get codelists from fixtures rather than HTTP Request
@pytest.fixture(autouse=True)
def mock_response(monkeypatch):
    """Don't use HTTP requests to get codelists."""

    def mock_get(lang, codelist_name):
        with open(os.path.join('tests', 'fixtures', "codelists", lang, f'{codelist_name}.json')) as codelist_file:
            codelist_data = json.load(codelist_file)
        return codelist_data

    monkeypatch.setattr(import_codelists, "get_codelist_from_request", mock_get)
