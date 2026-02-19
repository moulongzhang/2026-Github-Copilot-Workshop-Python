# ポモドーロタイマー Web アプリケーション アーキテクチャ案

## 概要

Flask（Python）をバックエンド、HTML/CSS/JavaScript をフロントエンドとして使用するポモドーロタイマー Web アプリケーション。セッションの進捗記録・取得は REST API 経由で行い、タイマー制御はフロントエンドで完結させるアーキテクチャを採用する。

---

## ディレクトリ構造

```
pomodoro/
├── app.py                        # Flaskアプリのエントリーポイント（Application Factory）
├── models/
│   └── session.py                # ポモドーロセッションのデータモデル
├── repositories/
│   ├── base.py                   # 抽象リポジトリ（インターフェース定義）
│   └── sqlite_repository.py     # SQLiteを使った具象リポジトリ
├── services/
│   └── pomodoro_service.py      # ビジネスロジックの集約
├── routes/
│   └── api.py                   # REST API エンドポイント
├── static/
│   ├── css/
│   │   └── style.css            # UIスタイル（パープル系グラデーション）
│   └── js/
│       ├── timerCore.js         # タイマーロジック（DOM非依存・テスト可能）
│       ├── timerUI.js           # DOM操作・イベントバインディング
│       └── progressRing.js     # 円形プログレスバー描画（SVG）
├── templates/
│   └── index.html              # メインページ（Single Page）
└── tests/
    ├── conftest.py             # pytestフィクスチャ共有
    ├── test_service.py         # サービス層のユニットテスト
    └── test_api.py             # APIエンドポイントのテスト
```

---

## レイヤー構成と責務

| レイヤー | 技術 | 役割 |
|---|---|---|
| **フロントエンド** | HTML / CSS / JavaScript | UI描画、タイマー制御、状態管理 |
| **バックエンド（ルート）** | Flask | HTTPリクエストの受付・レスポンス返却 |
| **バックエンド（サービス）** | Python | ビジネスロジックの処理 |
| **バックエンド（リポジトリ）** | Python + SQLite | セッションデータの永続化・取得 |

---

## REST API 設計

| メソッド | エンドポイント | 説明 |
|---|---|---|
| `GET` | `/api/stats` | 今日の進捗（完了数・集中時間）を取得 |
| `POST` | `/api/session/complete` | セッション完了を記録 |
| `POST` | `/api/session/reset` | セッションをリセット |

---

## フロントエンド設計

### タイマーの状態管理

タイマー制御はブラウザ側（`setInterval`）で行い、Flask はリアルタイム管理を持たない。

```
State: { mode: 'work' | 'break', remaining: 1500, isRunning: false }
  ↓
Timer tick → SVGプログレスリング更新 + 残り時間表示
  ↓
タイマー完了 → POST /api/session/complete → 今日の進捗を更新表示
```

### 円形プログレスバー

SVGの `<circle>` タグと `stroke-dashoffset` を使って描画する。

```js
// 進捗率に応じてオフセットを変化させる
circle.style.strokeDashoffset = circumference * (1 - progress);
```

### JS ファイルの責務分離（テスタビリティ向上）

- **`timerCore.js`** — DOM に依存しないピュアな関数（Jest でそのままテスト可能）
- **`timerUI.js`** — DOM操作・イベントバインディング
- **`progressRing.js`** — SVG描画ロジック

```js
// timerCore.js の例（DOM非依存）
export function tick(state) {
    if (!state.isRunning || state.remaining <= 0) return state;
    return { ...state, remaining: state.remaining - 1 };
}

export function isComplete(state) {
    return state.remaining <= 0;
}
```

---

## バックエンド設計

### Application Factory パターン（`app.py`）

テスト時に独立した設定でアプリを生成できるようにする。

```python
def create_app(config=None):
    app = Flask(__name__)
    if config:
        app.config.update(config)
    # ルート・DB初期化など
    return app
```

### Repository パターン

DB への依存を抽象化し、テスト時にインメモリ実装へ差し替え可能にする。

```python
# repositories/base.py
from abc import ABC, abstractmethod

class PomodoroRepositoryBase(ABC):
    @abstractmethod
    def get_today_stats(self) -> dict: ...

    @abstractmethod
    def record_session(self, duration_sec: int) -> None: ...
```

### Service レイヤー（`pomodoro_service.py`）

ビジネスロジックを Flask ルートから切り離し、単体テストを容易にする。

```python
class PomodoroService:
    def __init__(self, repo: PomodoroRepositoryBase):  # 依存性注入
        self.repo = repo

    def complete_session(self, duration_sec: int) -> dict:
        self.repo.record_session(duration_sec)
        return self.repo.get_today_stats()
```

### データモデル（`models/session.py`）

```python
class PomodoroSession:
    id: int
    date: date            # 記録日
    completed_count: int  # 完了したポモドーロ数
    total_focus_sec: int  # 累計集中時間（秒）
```

---

## テスト設計

### pytest フィクスチャ（`tests/conftest.py`）

```python
import pytest
from app import create_app

@pytest.fixture
def app():
    app = create_app(config={"TESTING": True, "DATABASE": ":memory:"})
    yield app

@pytest.fixture
def client(app):
    return app.test_client()
```

### テスト対象と方針

| テストファイル | 対象 | 方針 |
|---|---|---|
| `test_service.py` | `PomodoroService` | `InMemoryRepository` を注入してビジネスロジックを検証 |
| `test_api.py` | Flask エンドポイント | `test_client` でHTTPリクエスト/レスポンスを検証 |
| `timerCore.test.js` | `timerCore.js` | Jest でDOM非依存のピュアな関数を検証 |

---

## 実装順序（推奨）

1. `app.py` — Application Factory の骨格と静的ファイル配信
2. `models/session.py` + `repositories/` — データモデルとリポジトリ
3. `services/pomodoro_service.py` + `tests/test_service.py` — サービス層とテスト
4. `routes/api.py` + `tests/test_api.py` — APIエンドポイントとテスト
5. `index.html` + `style.css` — UIレイアウト（モックに忠実に）
6. `timerCore.js` + `progressRing.js` — タイマーロジックと円形プログレス
7. `timerUI.js` — DOM操作・API連携
