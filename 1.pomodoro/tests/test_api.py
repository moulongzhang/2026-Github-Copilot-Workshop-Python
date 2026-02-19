"""
test_api.py
API エンドポイントのテスト

フェーズ1時点では /api 配下にエンドポイントは未実装のため、
Blueprint の登録状態と、未定義ルートへのアクセス挙動を検証する。
フェーズ3で各エンドポイントのテストをこのファイルに追加する。
"""


class TestApiBlueprintRegistration:
    """/api Blueprint が正しく登録されていることのテスト。"""

    def test_api_blueprint_is_registered(self, app):
        """api Blueprint がアプリに登録されていることを確認する。"""
        blueprint_names = list(app.blueprints.keys())
        assert "api" in blueprint_names

    def test_undefined_api_route_returns_404(self, client):
        """/api 配下の未定義ルートが HTTP 404 を返すことを確認する。"""
        response = client.get("/api/undefined")
        assert response.status_code == 404

    def test_api_prefix_is_correct(self, app):
        """/api の url_prefix が正しく設定されていることを確認する。"""
        from routes.api import bp
        assert bp.url_prefix == "/api"
