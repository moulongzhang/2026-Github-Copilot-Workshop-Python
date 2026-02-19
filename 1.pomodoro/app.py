import os
from flask import Flask, render_template


def create_app(config=None):
    app = Flask(__name__)

    # デフォルト設定
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "pomodoro.db"),
    )

    # テスト・外部設定で上書き可能
    if config is not None:
        app.config.update(config)

    # instance フォルダが存在しない場合は作成
    os.makedirs(app.instance_path, exist_ok=True)

    # ルート登録
    from routes.api import bp as api_bp
    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    # macOS はポート5000をAirPlayが使用するため5001を使用
    app.run(debug=True, port=5001)
