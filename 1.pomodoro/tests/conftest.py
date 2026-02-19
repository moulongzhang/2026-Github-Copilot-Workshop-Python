import pytest
from app import create_app


@pytest.fixture
def app():
    """テスト用Flaskアプリを生成する。インメモリDBを使用。"""
    app = create_app(config={
        "TESTING": True,
        "DATABASE": ":memory:",
    })
    yield app


@pytest.fixture
def client(app):
    """テスト用HTTPクライアント。"""
    return app.test_client()
