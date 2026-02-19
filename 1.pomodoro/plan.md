# ポモドーロタイマー 段階的実装計画

## 方針

- 各フェーズは「動くものが手元にある」状態で完了とする
- フェーズ1〜3でバックエンドの土台を固め、フェーズ4〜6でフロントエンドを積み上げる
- 各フェーズ末にテストが通ることを確認してから次へ進む

---

## フェーズ1：プロジェクト骨格の構築

**目標：** Flask アプリが起動し、`index.html` が表示される

### タスク

- [ ] ディレクトリ構造の作成（`models/`, `repositories/`, `services/`, `routes/`, `static/`, `templates/`, `tests/`）
- [ ] `requirements.txt` の作成（`flask`, `pytest`, `pytest-flask`）
- [ ] `app.py` — Application Factory パターンで Flask アプリを作成
- [ ] `templates/index.html` — 空のHTMLページ（タイトルのみ）
- [ ] 動作確認：`flask run` でブラウザに画面が表示される

---

## フェーズ2：データ層の実装

**目標：** セッションデータをSQLiteに保存・取得できる

### タスク

- [ ] `models/session.py` — `PomodoroSession` データクラスの定義
- [ ] `repositories/base.py` — 抽象リポジトリ（`get_today_stats`, `record_session`）
- [ ] `repositories/sqlite_repository.py` — SQLite を使った具象リポジトリ
  - DB接続・テーブル作成（`CREATE TABLE IF NOT EXISTS`）
  - `record_session`: 当日レコードがあれば更新、なければ挿入
  - `get_today_stats`: 当日の完了数・集中時間を返す
- [ ] `tests/conftest.py` — インメモリDB用フィクスチャ
- [ ] `tests/test_repository.py` — リポジトリのユニットテスト

---

## フェーズ3：サービス層・APIの実装

**目標：** REST API が正しいJSONを返す

### タスク

- [ ] `services/pomodoro_service.py` — `PomodoroService` クラス（ビジネスロジック）
  - `complete_session(duration_sec)` — セッション記録 → 当日統計を返す
  - `get_stats()` — 当日統計を返す
- [ ] `routes/api.py` — REST APIエンドポイント
  - `GET /api/stats`
  - `POST /api/session/complete`
- [ ] `app.py` にルートを登録、DB初期化を接続
- [ ] `tests/test_service.py` — サービス層のユニットテスト（InMemory リポジトリ注入）
- [ ] `tests/test_api.py` — APIエンドポイントのテスト（`test_client` 使用）
- [ ] 動作確認：`curl` または `httpie` でAPIレスポンスを確認

---

## フェーズ4：UIレイアウトの実装

**目標：** モックに忠実な静的UIが表示される（タイマーは動かない）

### タスク

- [ ] `templates/index.html` — UIの全要素を配置
  - タイトル（ポモドーロタイマー）
  - モード表示ラベル（作業中）
  - SVG円形プログレスバー（初期状態）
  - 残り時間表示（`25:00`）
  - 「開始」「リセット」ボタン
  - 「今日の進捗」セクション（完了数・集中時間）
- [ ] `static/css/style.css` — モックに合わせたスタイリング
  - パープル系グラデーション背景（`#7c6fcd` 系）
  - ホワイトカードレイアウト
  - ボタンスタイル（塗りつぶし / アウトライン）
  - レスポンシブ対応

---

## フェーズ5：フロントエンド タイマーロジックの実装

**目標：** タイマーが動作し、円形プログレスバーが連動する

### タスク

- [ ] `static/js/timerCore.js` — DOM非依存のピュアなロジック
  - `tick(state)` — 1秒カウントダウン
  - `isComplete(state)` — タイマー完了判定
  - `formatTime(seconds)` — `MM:SS` 形式にフォーマット
  - `calcProgress(remaining, total)` — 進捗率（0〜1）を計算
- [ ] `static/js/progressRing.js` — SVG円形プログレスバー制御
  - `updateRing(progress)` — `stroke-dashoffset` を更新
- [ ] `static/js/timerUI.js` — DOM操作・イベント連携
  - 「開始/一時停止」ボタンのトグル
  - `setInterval` によるタイマーループ
  - `timerCore.js` と `progressRing.js` を呼び出し
  - タイマー完了時の処理（モード切替・作業→休憩）
- [ ] 動作確認：ブラウザでタイマーが動作する

---

## フェーズ6：フロントエンド〜API連携の実装

**目標：** セッション完了が記録され、今日の進捗が正しく表示される

### タスク

- [ ] `timerUI.js` にAPI呼び出しを追加
  - タイマー完了時 → `POST /api/session/complete`
  - ページロード時 → `GET /api/stats` で進捗を初期表示
- [ ] 「今日の進捗」セクションを取得データで動的に更新
  - 完了数（例：`4`）
  - 集中時間（例：`1時間40分`）
- [ ] エラーハンドリング（API失敗時のフォールバック表示）
- [ ] 動作確認：セッション完了 → 進捗が即時更新される

---

## フェーズ7：仕上げ・Nice to Have

**目標：** 完成度を高める

### タスク

- [ ] タイマー完了時のブラウザ通知（Web Notifications API）
- [ ] ボタン状態のアニメーション（ホバー・クリック）
- [ ] 全テストの通過確認（`pytest` + Jest）
- [ ] `README.md` にセットアップ手順を記載

---

## フェーズ別 完了条件まとめ

| フェーズ | 完了条件 |
|---|---|
| 1 | `flask run` でブラウザに画面表示 |
| 2 | `pytest tests/test_repository.py` 全テスト通過 |
| 3 | `pytest tests/` 全テスト通過、API が正しいJSONを返す |
| 4 | モックと同等のUIが静的に表示される |
| 5 | タイマーの開始・一時停止・リセット・自動切替が動作する |
| 6 | セッション完了が記録され今日の進捗が動的に更新される |
| 7 | 全テスト通過、通知動作、README完備 |
