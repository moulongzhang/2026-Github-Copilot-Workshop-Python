# Copilot Web Relay — 計画書

## 概要

ローカルで動作する GitHub Copilot CLI をブラウザからアクセス可能にする Web アプリケーション（Web Relay）を構築する。
ユーザーはブラウザ上のチャット UI を通じて Copilot CLI とリアルタイムにやり取りでき、ターミナルを直接操作することなく AI コーディング支援を受けられる。

## アーキテクチャ

```
┌──────────────┐    WebSocket     ┌──────────────────┐     PTY/stdin/stdout     ┌──────────────┐
│   Browser    │ ◄──────────────► │  Backend Server  │ ◄────────────────────►   │  Copilot CLI │
│  (React/TS)  │    (双方向通信)    │  (Python/FastAPI)│      (子プロセス管理)      │   (copilot)  │
└──────────────┘                  └──────────────────┘                          └──────────────┘
```

### コンポーネント構成

| コンポーネント | 技術スタック | 役割 |
|---|---|---|
| **Frontend** | React + TypeScript + Vite | チャット UI、ターミナル表示、セッション管理 |
| **Backend** | Python (FastAPI) + WebSocket | Copilot CLI プロセスの管理、WebSocket ブリッジ |
| **CLI Bridge** | Python (asyncio + pty) | Copilot CLI の PTY 制御、入出力のストリーミング |

## 機能要件

### Phase 1: MVP（最小限の実用プロダクト）

1. **CLI プロセス管理**
   - Copilot CLI (`copilot`) の子プロセス起動・停止
   - PTY（疑似端末）を使った入出力制御
   - ANSI エスケープシーケンスの処理

2. **WebSocket ブリッジ**
   - ブラウザ ↔ バックエンド間のリアルタイム双方向通信
   - CLI の stdout/stderr をブラウザへストリーミング
   - ブラウザからの入力を CLI の stdin へ転送

3. **Web UI（基本）**
   - ターミナルエミュレータ表示（xterm.js ベース）
   - 接続状態インジケータ
   - セッション開始・終了ボタン

### Phase 2: チャット UI 強化

4. **チャットインターフェース**
   - チャット形式の UI（ユーザー入力 / Copilot 応答の分離表示）
   - Markdown レンダリング（コードブロック、シンタックスハイライト）
   - コード差分のビジュアル表示

5. **セッション管理**
   - 複数セッションの並行管理
   - セッション履歴の保存・復元
   - セッション一覧表示

### Phase 3: 高度な機能

6. **認証・セキュリティ**
   - ローカルネットワーク内のアクセス制御
   - トークンベース認証（オプション）
   - CORS 設定

7. **ファイル連携**
   - ブラウザからのファイルアップロード → CLI ワークスペースへ配置
   - CLI が編集したファイルのプレビュー
   - `/diff` コマンド結果のビジュアル表示

8. **UI/UX の洗練**
   - レスポンシブデザイン
   - ダークモード / ライトモード
   - キーボードショートカット対応

## 技術詳細

### Backend（Python / FastAPI）

```
copilotWebRelay/
├── backend/
│   ├── main.py              # FastAPI アプリケーションのエントリポイント
│   ├── cli_bridge.py        # Copilot CLI プロセス管理（PTY 制御）
│   ├── websocket_handler.py # WebSocket ハンドラ（メッセージルーティング + ステータス応答）
│   ├── config.py            # 設定（dataclass で一元管理）
│   └── requirements.txt     # Python 依存関係
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # メインアプリ（ターミナル UI + WebSocket 接続 + セッション管理）
│   │   ├── App.css          # ダークテーマ、ツールバー、レイアウト
│   │   ├── main.tsx         # React エントリポイント
│   │   └── index.css        # グローバルリセットスタイル
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts       # Vite 設定 + WebSocket プロキシ
├── e2e/                     # Playwright E2E テスト
│   ├── tests/
│   │   └── start-session.spec.ts
│   ├── playwright.config.ts
│   └── package.json
├── docs/
│   ├── planning.md          # 本ドキュメント
│   ├── develop1.md          # Phase 1 実装記録
│   └── develop2.md          # Start Session バグ修正記録
└── README.md
```

### 主要な依存関係

**Backend:**
- `fastapi` — Web フレームワーク
- `uvicorn` — ASGI サーバー
- `websockets` — WebSocket サポート（FastAPI 内蔵）
- `ptyprocess` または `pexpect` — PTY 制御

**Frontend:**
- `react` + `typescript` — UI フレームワーク
- `xterm.js` + `@xterm/addon-fit` — ターミナルエミュレータ
- `react-markdown` — Markdown レンダリング（Phase 2）
- `vite` — ビルドツール

### WebSocket プロトコル設計

```json
// クライアント → サーバー
{
  "type": "input",          // ユーザー入力
  "payload": "string"
}
{
  "type": "resize",         // ターミナルリサイズ
  "cols": 80,
  "rows": 24
}
{
  "type": "session",        // セッション操作
  "action": "start | stop",
  "cols": 120,              // start 時のみ: 初期ターミナル幅
  "rows": 40                // start 時のみ: 初期ターミナル高さ
}

// サーバー → クライアント
{
  "type": "output",         // CLI 出力
  "payload": "string"
}
{
  "type": "status",         // セッション状態の変化通知
  "payload": "string",      // 人間向けメッセージ（例: "Session started"）
  "state": "running | stopped | error"
}
```

> **注意**: フロントエンドの UI 状態（`sessionActive` 等）は、送信時に楽観的に更新するのではなく、サーバーからの `status` メッセージの `state` に基づいて更新すること。CLI プロセスの起動は失敗しうるため、サーバー確認応答が必須。

### CLI Bridge の動作フロー

1. ブラウザが WebSocket 接続を確立
2. ユーザーが「Start Session」をクリック → `session:start` メッセージ送信
3. バックエンドが PTY を作成し `copilot` プロセスを起動（`pexpect.spawn` — 失敗時は `status:error` を返す）
4. 起動成功時に `status:running` をブラウザへ送信 → フロントエンドが `sessionActive = true` に更新
5. PTY の stdout を `asyncio.Queue` 経由で監視し、出力を WebSocket 経由でブラウザへ送信
6. ブラウザからの入力を PTY の stdin へ書き込み（`run_in_executor` でブロッキング回避）
7. プロセス終了時に `status:stopped` を送信

### 実装上の重要な注意事項

以下は Phase 1 の実装・デバッグを通じて判明した、設計段階で把握すべき注意点です。

#### Vite WebSocket プロキシ設定

開発モードでは Vite の dev server がフロントエンドを配信するため、`/ws` へのリクエストをバックエンド（port 8000）にプロキシする必要がある。**`target` は `http://` で指定すること**（`ws://` ではない）。Vite 内部の `http-proxy` モジュールが HTTP URL から WebSocket Upgrade を自動処理する。

```typescript
// vite.config.ts
server: {
  proxy: {
    '/ws': {
      target: 'http://localhost:8000',  // ✅ http:// を使う
      ws: true,
    },
  },
},
```

#### React StrictMode と WebSocket のライフサイクル

React 18/19 の StrictMode は開発モードで `useEffect` を2回実行する（マウント → クリーンアップ → 再マウント）。WebSocket を `useEffect` 内で作成する場合、古い接続の `onclose` コールバックが新しい接続の ref を破壊する問題が発生する。

**対策**: `onopen` / `onclose` / `onerror` ハンドラ内で、`wsRef.current === ws`（ref が自分自身を指しているか）を確認してから状態を更新する。

```typescript
ws.onclose = () => {
  if (wsRef.current === ws) {  // 古い接続のコールバックを無視
    setStatus('disconnected');
    wsRef.current = null;
  }
};
```

#### CLI プロセス起動のエラーハンドリング

`pexpect.spawn()` は `copilot` コマンドが見つからない場合や PTY 作成に失敗した場合に例外を投げる。`cli_bridge.py` で `try/except` で囲み、`websocket_handler.py` から `status:error` メッセージとしてブラウザに伝搬させる。

## 実装タスク一覧

### Phase 1: MVP

| ID | タスク | 依存 | 説明 |
|---|---|---|---|
| `p1-project-setup` | プロジェクト初期セットアップ | — | ディレクトリ構造、依存関係の定義、開発環境構築 |
| `p1-cli-bridge` | CLI Bridge 実装 | p1-project-setup | PTY を使った Copilot CLI の起動・入出力制御 |
| `p1-websocket-server` | WebSocket サーバー実装 | p1-project-setup | FastAPI WebSocket エンドポイントの実装 |
| `p1-relay-integration` | Relay 統合 | p1-cli-bridge, p1-websocket-server | CLI Bridge と WebSocket の接続 |
| `p1-frontend-terminal` | フロントエンド（ターミナル） | p1-project-setup | xterm.js ベースのターミナル UI |
| `p1-frontend-websocket` | フロントエンド WebSocket 接続 | p1-frontend-terminal | WebSocket クライアントの実装 |
| `p1-e2e-test` | E2E テスト・動作確認 | p1-relay-integration, p1-frontend-websocket | Playwright で WebSocket フレーム監視を含む結合テスト |

### Phase 2: チャット UI 強化

| ID | タスク | 依存 | 説明 |
|---|---|---|---|
| `p2-chat-ui` | チャット UI 実装 | p1-e2e-test | チャット形式の表示コンポーネント |
| `p2-markdown-render` | Markdown レンダリング | p2-chat-ui | Copilot 応答の Markdown 表示 |
| `p2-session-mgmt` | セッション管理 | p1-e2e-test | 複数セッション対応 |
| `p2-history` | 履歴機能 | p2-session-mgmt | セッション履歴の保存と表示 |

### Phase 3: 高度な機能

| ID | タスク | 依存 | 説明 |
|---|---|---|---|
| `p3-auth` | 認証機能 | p2-session-mgmt | アクセス制御の実装 |
| `p3-file-integration` | ファイル連携 | p2-chat-ui | ファイルアップロード・プレビュー |
| `p3-ui-polish` | UI/UX 改善 | p2-chat-ui | レスポンシブ、テーマ対応 |

## 確認が必要な事項

以下の点について方針の確認が必要です：

### 1. 技術スタックの確認
- **Backend**: Python (FastAPI) を想定していますが、Node.js (Express) の方が好ましいですか？
- **Frontend**: React + TypeScript を想定していますが、他のフレームワーク（Vue.js, Svelte 等）の希望はありますか？

### 2. デプロイ形態
- ローカルマシン上でのみ動作する前提ですか？（`localhost` アクセスのみ）
- 同一ネットワーク内の他デバイスからのアクセスも想定しますか？
- Docker コンテナ化は必要ですか？

### 3. ユーザー想定
- シングルユーザー前提ですか？複数ユーザーの同時利用は想定しますか？
- 認証機能の優先度はどの程度ですか？

### 4. Copilot CLI の認証
- Copilot CLI の GitHub 認証はサーバー側で事前に完了している前提ですか？
- ブラウザから GitHub 認証フローを実行する必要はありますか？

### 5. スコープの優先度
- Phase 1 (ターミナルエミュレータ) と Phase 2 (チャット UI) のどちらを優先しますか？
- MVP として最低限必要な機能セットは上記で合っていますか？

### 6. 既存リポジトリとの関係
- 本リポジトリ（Python ワークショップ）のコードとの連携は必要ですか？
- `copilotWebRelay/` はこのリポジトリ内に配置する前提でよいですか？

## 開発環境の前提

- **OS**: Linux（GitHub Codespaces / Dev Containers）
- **Python**: 3.10+
- **Node.js**: 18+ (フロントエンド開発用)
- **Copilot CLI**: インストール済み、認証済みであること
