# ポモドーロタイマー Web アプリケーション アーキテクチャ設計書

## 概要

Flask + HTML/CSS/JavaScript を使用したポモドーロタイマーWebアプリケーションの設計書。
クライアントサイド重視型のアーキテクチャにより、リアルタイム性とユーザー体験を最適化する。

---

## 1. アーキテクチャパターン

### 採用パターン: **クライアントサイド重視型 + REST API**

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Browser)                    │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │   timer.js  │  │    ui.js     │  │ api-client.js │  │
│  │ (Core Logic)│  │ (UI Control) │  │  (API Calls)  │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
│         │                 │                  │           │
│         └─────────────────┴──────────────────┘           │
│                           │                              │
└───────────────────────────┼──────────────────────────────┘
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Backend (Flask)                        │
│  ┌──────────────┐  ┌─────────────┐  ┌────────────────┐ │
│  │   routes/    │  │  services/  │  │   models.py    │ │
│  │  api.py      │─▶│ timer_      │─▶│  (Optional)    │ │
│  │  views.py    │  │ service.py  │  │                │ │
│  └──────────────┘  └─────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  Data Storage   │
                   │ (JSON / SQLite) │
                   └─────────────────┘
```

### 選定理由

1. **パフォーマンス**: タイマーは1秒ごとに更新されるため、クライアントサイドで処理することでサーバー負荷を削減
2. **レスポンシブ**: サーバーとの通信を最小限にし、即座にUIが反応
3. **オフライン対応**: LocalStorageと組み合わせることで、基本機能がオフラインでも動作
4. **スケーラビリティ**: 将来的にPWA化やモバイルアプリ化が容易
5. **シンプル性**: 複雑な状態同期が不要で、実装と保守が容易

---

## 2. ディレクトリ構造

```
1.pomodoro/
├── app.py                          # Flaskアプリケーションのエントリーポイント
├── config.py                       # 設定ファイル（デフォルト値、環境変数）
├── models.py                       # データモデル（DB使用時）
│
├── routes/                         # ルーティング層
│   ├── __init__.py
│   ├── api.py                      # RESTful API エンドポイント
│   └── views.py                    # ページレンダリング用ルート
│
├── services/                       # ビジネスロジック層
│   ├── __init__.py
│   └── timer_service.py            # 統計計算、セッション管理
│
├── static/                         # 静的ファイル
│   ├── css/
│   │   ├── style.css               # メインスタイルシート
│   │   ├── animations.css          # アニメーション用CSS
│   │   └── responsive.css          # レスポンシブデザイン
│   ├── js/
│   │   ├── timer.js                # タイマーコアロジック
│   │   ├── ui.js                   # UI制御・イベントハンドラ
│   │   └── api-client.js           # APIクライアント
│   └── sounds/
│       └── notification.mp3        # 通知音
│
├── templates/                      # Jinja2テンプレート
│   ├── base.html                   # ベーステンプレート
│   └── index.html                  # メインページ
│
└── data/                           # データ永続化
    ├── settings.json               # ユーザー設定
    └── sessions.json               # セッション履歴（簡易版）
```

---

## 3. コンポーネント設計

### 3.1 バックエンド (Flask)

#### 3.1.1 app.py - アプリケーションエントリーポイント

**責務:**
- Flaskアプリケーションの初期化
- ルート登録
- CORS設定（必要に応じて）
- エラーハンドラ登録
- サーバー起動

**主要な設定:**
```python
- DEBUG モード
- SECRET_KEY
- JSON エンコーディング設定
- 静的ファイルパス
```

#### 3.1.2 routes/api.py - REST API エンドポイント

**API エンドポイント設計:**

| メソッド | エンドポイント | 説明 | リクエスト | レスポンス |
|---------|--------------|------|-----------|-----------|
| GET | `/api/settings` | 設定取得 | - | `{ work_duration: 25, ... }` |
| POST | `/api/settings` | 設定保存 | `{ work_duration: 25, ... }` | `{ success: true }` |
| GET | `/api/sessions` | セッション履歴取得 | `?date=2026-02-24` | `[{ id, type, duration, ... }]` |
| POST | `/api/sessions` | セッション記録保存 | `{ type, duration, ... }` | `{ id, success: true }` |
| GET | `/api/stats` | 統計情報取得 | `?period=today` | `{ total_pomodoros, total_time, ... }` |

**エラーレスポンス形式:**
```json
{
  "error": "エラーメッセージ",
  "status": 400
}
```

#### 3.1.3 routes/views.py - ページレンダリング

**責務:**
- メインページのレンダリング
- 初期設定の注入

**エンドポイント:**
- `GET /` - メインページ表示

#### 3.1.4 services/timer_service.py - ビジネスロジック

**責務:**
- セッション履歴の集計
- 統計情報の計算
- データの検証とフォーマット

**主要関数:**
```python
- get_settings() -> dict
- save_settings(settings: dict) -> bool
- save_session(session_data: dict) -> str
- get_sessions(date: str = None) -> list
- calculate_stats(period: str) -> dict
```

#### 3.1.5 config.py - 設定管理

**デフォルト設定:**
```python
DEFAULT_SETTINGS = {
    "work_duration": 25,              # 作業時間（分）
    "short_break": 5,                 # 短い休憩（分）
    "long_break": 15,                 # 長い休憩（分）
    "long_break_interval": 4,         # 長い休憩までのサイクル数
    "auto_start_breaks": False,       # 自動で休憩開始
    "auto_start_pomodoros": False,    # 自動で作業開始
    "sound_enabled": True,            # 通知音の有効化
    "notification_enabled": True      # ブラウザ通知の有効化
}
```

---

### 3.2 フロントエンド (JavaScript)

#### 3.2.1 timer.js - タイマーコアロジック

**PomodoroTimer クラス設計:**

```javascript
class PomodoroTimer {
  constructor(settings) {
    this.settings = settings;
    this.state = {
      mode: 'work',              // work | short-break | long-break
      timeRemaining: 0,          // 秒単位
      isRunning: false,
      completedPomodoros: 0
    };
    this.intervalId = null;
    this.callbacks = {};
  }

  // 主要メソッド
  start()                          // タイマー開始
  pause()                          // タイマー一時停止
  reset()                          // タイマーリセット
  skip()                           // 現在のセッションをスキップ
  
  // 内部メソッド
  tick()                           // 1秒ごとの処理
  switchMode()                     // モード切り替え
  completeSession()                // セッション完了処理
  
  // イベント登録
  on(event, callback)              // イベントリスナー登録
  emit(event, data)                // イベント発火
}

// イベント種類
// - 'tick': { timeRemaining, mode }
// - 'complete': { mode, completedPomodoros }
// - 'modeChange': { newMode, oldMode }
// - 'start': {}
// - 'pause': {}
```

#### 3.2.2 ui.js - UI制御

**責務:**
- タイマー表示の更新
- ボタンの有効/無効制御
- 進捗バーのアニメーション
- モード切り替えの視覚効果
- 設定モーダルの表示/非表示
- 通知の表示

**主要関数:**
```javascript
- updateTimerDisplay(minutes, seconds)
- updateProgressBar(progress)
- updateModeDisplay(mode)
- toggleButtons(isRunning)
- showNotification(message)
- playSound()
- openSettingsModal()
- closeSettingsModal()
- renderStats(stats)
```

#### 3.2.3 api-client.js - API通信

**責務:**
- サーバーとのHTTP通信
- エラーハンドリング
- レスポンスのキャッシング（必要に応じて）

**主要関数:**
```javascript
- async fetchSettings()
- async saveSettings(settings)
- async saveSession(sessionData)
- async fetchSessions(date)
- async fetchStats(period)
- handleApiError(error)
```

---

## 4. データモデル

### 4.1 Settings (設定)

```json
{
  "work_duration": 25,
  "short_break": 5,
  "long_break": 15,
  "long_break_interval": 4,
  "auto_start_breaks": false,
  "auto_start_pomodoros": false,
  "sound_enabled": true,
  "notification_enabled": true
}
```

**制約:**
- `work_duration`: 1-120 (分)
- `short_break`: 1-60 (分)
- `long_break`: 1-60 (分)
- `long_break_interval`: 2-10 (回)

### 4.2 Session (セッション)

```json
{
  "id": "uuid-v4",
  "type": "work|short-break|long-break",
  "duration": 1500,
  "completed": true,
  "started_at": "2026-02-24T10:00:00Z",
  "ended_at": "2026-02-24T10:25:00Z"
}
```

### 4.3 Stats (統計)

```json
{
  "period": "today|week|month",
  "total_pomodoros": 8,
  "total_work_time": 12000,
  "total_break_time": 1800,
  "completion_rate": 0.95,
  "sessions": [...]
}
```

---

## 5. 状態管理

### 5.1 アプリケーション状態

```javascript
const AppState = {
  timer: {
    mode: 'work',
    timeRemaining: 1500,
    isRunning: false,
    completedPomodoros: 0,
    currentSessionStartTime: null
  },
  settings: {
    // Settings オブジェクト
  },
  ui: {
    showSettings: false,
    showStats: false
  },
  sessions: []
};
```

### 5.2 状態の永続化

- **クライアント**: LocalStorageに設定を保存（バックアップ）
- **サーバー**: JSON/SQLiteにセッション履歴と設定を保存
- **同期**: アプリ起動時にサーバーから設定を読み込み、LocalStorageと比較

---

## 6. 技術スタック

### 6.1 バックエンド

| 技術 | バージョン | 用途 |
|-----|----------|------|
| Python | 3.11+ | 実行環境 |
| Flask | 3.x | Webフレームワーク |
| flask-cors | 最新 | CORS対応（必要時） |
| python-dotenv | 最新 | 環境変数管理 |

**データベース（オプション）:**
- 簡易版: JSON ファイル
- 拡張版: SQLite + SQLAlchemy
- 本番版: PostgreSQL

### 6.2 フロントエンド

| 技術 | 用途 |
|-----|------|
| Vanilla JavaScript (ES6+) | ロジック実装 |
| CSS3 (Flexbox/Grid) | レイアウト |
| Web Notification API | ブラウザ通知 |
| Audio API | 通知音再生 |
| LocalStorage API | クライアント側設定保存 |

**CSSフレームワーク:**
- なし（カスタムCSS）または
- 軽量ユーティリティCSS（検討）

---

## 7. セキュリティ設計

### 7.1 対策項目

1. **入力検証**
   - 設定値の範囲チェック
   - 型チェック（数値、真偽値）
   - サニタイゼーション

2. **CSRF対策**
   - Flask-WTForms使用
   - またはCSRFトークン実装

3. **XSS対策**
   - Jinja2の自動エスケープ活用
   - ユーザー入力の適切なエスケープ

4. **認証・認可**
   - Phase 1: 不要（単一ユーザー）
   - Phase 2: セッション認証実装（マルチユーザー対応時）

5. **エラーハンドリング**
   - 詳細なエラーメッセージは開発環境のみ
   - 本番環境では一般的なメッセージ

### 7.2 環境変数管理

```python
# .env ファイル例
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///pomodoro.db
```

---

## 8. 実装フェーズ

### Phase 1: MVP（最小限の実装）

**目標**: 基本的なタイマー機能を動作させる

- [ ] Flaskアプリケーション基本構造
- [ ] 静的ファイル配信
- [ ] タイマーロジック（開始/停止/リセット）
- [ ] 作業/休憩モード切り替え
- [ ] シンプルなUI実装

**期間**: 1-2日

### Phase 2: 設定機能

**目標**: カスタマイズ可能にする

- [ ] 設定モーダルUI
- [ ] 設定のAPI実装
- [ ] 設定の永続化（JSON）
- [ ] フォームバリデーション

**期間**: 1日

### Phase 3: 体験向上

**目標**: ユーザー体験を改善

- [ ] 通知音実装
- [ ] ブラウザ通知実装
- [ ] 進捗バーとアニメーション
- [ ] レスポンシブデザイン
- [ ] アクセシビリティ対応

**期間**: 2-3日

### Phase 4: 分析機能

**目標**: 生産性を可視化

- [ ] セッション履歴の記録
- [ ] 統計情報API
- [ ] グラフ表示（Chart.js等）
- [ ] 日別/週別/月別表示

**期間**: 2-3日

---

## 9. テスト戦略

### 9.1 バックエンドテスト

```python
# unittest または pytest を使用
- API エンドポイントのテスト
- ビジネスロジックの単体テスト
- データ検証のテスト
```

### 9.2 フロントエンドテスト

```javascript
// Jest または Mocha を使用（オプション）
- タイマーロジックの単体テスト
- UI関数のテスト
```

### 9.3 E2Eテスト

- Selenium または Playwright（オプション）
- 主要なユーザーフローのテスト

---

## 10. パフォーマンス最適化

### 10.1 フロントエンド

- CSSとJSの最小化（本番環境）
- 画像の最適化
- ブラウザキャッシュの活用
- 不要な再レンダリングの削減

### 10.2 バックエンド

- 静的ファイルのキャッシュ設定
- JSONファイルの読み書き最適化
- 必要に応じてデータベースインデックス

---

## 11. 拡張性の考慮点

### 11.1 将来的な機能追加

- **ユーザー認証**: 複数ユーザー対応
- **タスク管理**: ポモドーロとタスクの紐付け
- **チーム機能**: グループでのポモドーロ共有
- **カスタムテーマ**: ダークモード等
- **データエクスポート**: CSV/JSONでのエクスポート
- **統合**: CalendarAPI、Trello等との連携

### 11.2 アーキテクチャの進化

- **PWA化**: Service Workerでオフライン対応強化
- **WebSocket**: リアルタイム同期（チーム機能用）
- **マイクロサービス**: 統計機能の分離
- **CDN**: 静的ファイルの配信最適化

---

## 12. 開発環境

### 12.1 必要なツール

```bash
# Python環境
python 3.11+
pip
venv

# エディタ
VS Code (推奨)
  - Python extension
  - Flask Snippets
  - Prettier (JavaScript/CSS)

# デバッグツール
ブラウザ DevTools
Flask Debug Toolbar（開発時）
```

### 12.2 開発フロー

```bash
# 環境構築
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 開発サーバー起動
flask run --debug

# テスト実行
python -m pytest

# 本番ビルド（将来）
# 静的ファイルの最小化など
```

---

## 13. デプロイメント

### 13.1 開発環境

- Flask開発サーバー
- ローカルホスト

### 13.2 本番環境（将来）

**オプション1: PaaS（推奨）**
- Heroku
- Render
- Railway

**オプション2: VPS**
- Gunicorn + Nginx
- Supervisor（プロセス管理）

**オプション3: コンテナ**
- Docker
- Docker Compose

---

## 14. まとめ

このアーキテクチャは以下の特徴を持つ:

✅ **シンプル**: 学習コストが低く、保守が容易  
✅ **高速**: クライアントサイドでの処理により即座に反応  
✅ **拡張可能**: モジュール化により機能追加が容易  
✅ **実用的**: オフライン対応と通知機能で実際に使える  
✅ **段階的**: MVPから始めて段階的に機能追加可能  

このアーキテクチャに基づいて実装を進めることで、高品質なポモドーロタイマーアプリケーションを構築できます。
