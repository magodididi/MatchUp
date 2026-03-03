# tests/conftest.py
import pytest
import os
import shutil
import tempfile
from flask import Flask
from auth.routes import auth
from utils.storage import load_users, save_users, DATA_FILE

@pytest.fixture(autouse=True)
def temp_storage(monkeypatch, tmp_path):
    """Патчим DATA_FILE на временный файл для каждого теста"""
    test_json = tmp_path / "users_test.json"
    monkeypatch.setattr("utils.storage.DATA_FILE", str(test_json))
    if test_json.exists():
        test_json.unlink()
    save_users({})
    yield

@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "testkey"
    app.register_blueprint(auth)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()