# Copilot Web Relay

ローカルで動作する GitHub Copilot CLI をブラウザからアクセス可能にする Web アプリケーションです。
ブラウザ上のターミナル UI を通じて Copilot CLI とリアルタイムにやり取りでき、ターミナルを直接操作することなく AI コーディング支援を受けられます。

## アーキテクチャ

```
┌──────────────┐    WebSocket     ┌──────────────────┐     PTY/stdin/stdout     ┌──────────────┐
│   Browser    │ ◄──────────────► │  Backend Server  │ ◄────────────────────►   │  Copilot CLI │
│  (React/TS)  │    (双方向通信)    │  (Python/FastAPI)│      (子プロセス管理)      │   (copilot)  │
└──────────────┘                  └──────────────────┘                          └──────────────┘
```

| コンポーネント | 技術スタック | 役割 |
|---|---|---|
| **Frontend** | React + TypeScript + Vite + xterm.js | ターミナル UI、接続管理、セッション制御 |
| **Backend** | Python (FastAPI) + WebSocket + pexpect | Copilot CLI プロセス管理、WebSocket ブリッジ |

## 必要環境

- Python 3.10+
- Node.js 18+
- GitHub Copilot CLI（`copilot` コマンドが利用可能であること）

## セットアップ

### バックエンド

```bash
cd backend
pip install -r requirements.txt
```

### フロントエンド

```bash
cd frontend
npm install
```

## 起動方法

### 1. バックエンドを起動

```bash
cd backend
python main.py
```

バックエンドは `http://localhost:8000` で起動します。

### 2. フロントエンドを起動

```bash
cd frontend
npm run dev
```

### 3. ブラウザでアクセス

`http://localhost:5173` を開きます。「Start Session」ボタンをクリックすると Copilot CLI セッションが開始されます。

## E2E テスト実行方法

### セットアップ

```bash
cd e2e
npm install
npx playwright install chromium
```

### テスト実行

バックエンドとフロントエンドを起動した状態で：

```bash
cd e2e
npm test
```

ブラウザ表示付きで実行する場合：

```bash
npm run test:headed
```

## WebSocket プロトコル

フロントエンドとバックエンド間は WebSocket（`/ws`）で通信します。

### クライアント → サーバー

| type | 説明 | フィールド |
|---|---|---|
| `session` | セッション操作 | `action`: `"start"` / `"stop"`, `cols`, `rows` |
| `input` | ユーザー入力 | `payload`: 入力文字列 |
| `resize` | ターミナルリサイズ | `cols`, `rows` |

### サーバー → クライアント

| type | 説明 | フィールド |
|---|---|---|
| `output` | CLI 出力 | `payload`: 出力文字列 |
| `status` | 状態変化通知 | `payload`: メッセージ, `state`: `"running"` / `"stopped"` / `"error"` |

## プロジェクト構成

```
copilotWebRelay/
├── backend/
│   ├── main.py              # FastAPI エントリポイント
│   ├── cli_bridge.py        # Copilot CLI プロセス管理（PTY 制御）
│   ├── websocket_handler.py # WebSocket ハンドラ
│   ├── config.py            # 設定
│   └── requirements.txt     # Python 依存関係
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # メインアプリ（ターミナル + WebSocket + セッション管理）
│   │   ├── App.css          # ダークテーマスタイル
│   │   ├── main.tsx         # React エントリポイント
│   │   └── index.css        # グローバルスタイル
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts       # Vite 設定 + WebSocket プロキシ
├── e2e/
│   ├── tests/
│   │   └── start-session.spec.ts  # E2E テスト
│   ├── playwright.config.ts
│   └── package.json
├── planning.md              # 設計ドキュメント
└── README.md                # 本ファイル
```
