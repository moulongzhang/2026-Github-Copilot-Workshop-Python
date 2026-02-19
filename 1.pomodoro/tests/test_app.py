"""
test_app.py
Application Factory および index ルートのテスト
"""
from app import create_app


class TestCreateApp:
    """create_app() のテスト。"""

    def test_returns_flask_app(self):
        """create_app() が Flask アプリインスタンスを返すことを確認する。"""
        from flask import Flask
        app = create_app()
        assert isinstance(app, Flask)

    def test_testing_flag_is_set(self):
        """TESTING=True が正しくアプリに反映されることを確認する。"""
        app = create_app(config={"TESTING": True})
        assert app.config["TESTING"] is True

    def test_default_database_config_is_set(self):
        """DATABASE 設定がデフォルトで存在することを確認する。"""
        app = create_app()
        assert "DATABASE" in app.config

    def test_custom_database_config_overrides_default(self):
        """カスタム DATABASE 設定でデフォルト値が上書きされることを確認する。"""
        app = create_app(config={"DATABASE": ":memory:"})
        assert app.config["DATABASE"] == ":memory:"

    def test_config_none_does_not_raise(self):
        """config=None でも例外が発生しないことを確認する。"""
        app = create_app(config=None)
        assert app is not None


class TestIndexRoute:
    """/ ルートのテスト。"""

    def test_index_returns_200(self, client):
        """/ へのGETリクエストが HTTP 200 を返すことを確認する。"""
        response = client.get("/")
        assert response.status_code == 200

    def test_index_returns_html(self, client):
        """レスポンスの Content-Type が text/html であることを確認する。"""
        response = client.get("/")
        assert "text/html" in response.content_type

    def test_index_contains_title(self, client):
        """レスポンスボディにアプリのタイトルが含まれることを確認する。"""
        response = client.get("/")
        assert "ポモドーロタイマー" in response.data.decode("utf-8")

    def test_index_contains_charset_utf8(self, client):
        """HTML の charset が UTF-8 であることを確認する。"""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "UTF-8" in html or "utf-8" in html

    def test_post_to_index_returns_405(self, client):
        """/ への POST リクエストが HTTP 405 を返すことを確認する。"""
        response = client.post("/")
        assert response.status_code == 405
