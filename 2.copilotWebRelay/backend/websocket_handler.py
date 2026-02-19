import asyncio
import json
import logging

from fastapi import WebSocket, WebSocketDisconnect

from cli_bridge import CLIBridge
from config import config

logger = logging.getLogger(__name__)


async def _send_json(ws: WebSocket, data: dict) -> None:
    await ws.send_text(json.dumps(data))


async def _output_forwarder(ws: WebSocket, queue: asyncio.Queue) -> None:
    """Queueからデータを取り出し、WebSocketへ送信するバックグラウンドタスク。"""
    try:
        while True:
            data = await queue.get()
            await _send_json(ws, {"type": "output", "payload": data})
    except Exception:
        pass


async def handle_websocket(websocket: WebSocket) -> None:
    await websocket.accept()

    bridge = CLIBridge()
    queue: asyncio.Queue = asyncio.Queue()
    reader_task: asyncio.Task | None = None
    forwarder_task: asyncio.Task | None = None

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type", "")

            if msg_type == "session":
                action = msg.get("action", "")

                if action == "start":
                    cols = msg.get("cols", config.DEFAULT_COLS)
                    rows = msg.get("rows", config.DEFAULT_ROWS)
                    ok = bridge.start(cols, rows)
                    if ok:
                        # 出力読み取りとWebSocket転送のタスクを開始
                        reader_task = asyncio.create_task(bridge.read_output(queue))
                        forwarder_task = asyncio.create_task(
                            _output_forwarder(websocket, queue)
                        )
                        await _send_json(websocket, {
                            "type": "status",
                            "payload": "Session started",
                            "state": "running",
                        })
                    else:
                        await _send_json(websocket, {
                            "type": "status",
                            "payload": "Failed to start CLI process",
                            "state": "error",
                        })

                elif action == "stop":
                    bridge.stop()
                    if reader_task:
                        reader_task.cancel()
                    if forwarder_task:
                        forwarder_task.cancel()
                    reader_task = None
                    forwarder_task = None
                    await _send_json(websocket, {
                        "type": "status",
                        "payload": "Session stopped",
                        "state": "stopped",
                    })

            elif msg_type == "input":
                payload = msg.get("payload", "")
                await bridge.write(payload)

            elif msg_type == "resize":
                cols = msg.get("cols", config.DEFAULT_COLS)
                rows = msg.get("rows", config.DEFAULT_ROWS)
                bridge.resize(cols, rows)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error("WebSocket error: %s", e)
    finally:
        # クリーンアップ
        if reader_task:
            reader_task.cancel()
        if forwarder_task:
            forwarder_task.cancel()
        bridge.stop()
