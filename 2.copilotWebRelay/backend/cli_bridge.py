import asyncio
import logging

import pexpect

from config import config

logger = logging.getLogger(__name__)


class CLIBridge:
    def __init__(self) -> None:
        self.process: pexpect.spawn | None = None

    @property
    def is_alive(self) -> bool:
        return self.process is not None and self.process.isalive()

    def start(self, cols: int | None = None, rows: int | None = None) -> bool:
        """CLIプロセスをPTY経由で起動する。成功時True、失敗時Falseを返す。"""
        if self.is_alive:
            return True

        cols = cols or config.DEFAULT_COLS
        rows = rows or config.DEFAULT_ROWS

        try:
            self.process = pexpect.spawn(
                config.COPILOT_CMD,
                encoding="utf-8",
                dimensions=(rows, cols),
                timeout=5,
            )
            # プロセスが即座に終了していないか確認
            if not self.process.isalive():
                logger.error("CLI process exited immediately")
                self.process = None
                return False
            logger.info("CLI process started (pid=%s)", self.process.pid)
            return True
        except (pexpect.ExceptionPexpect, FileNotFoundError, OSError) as e:
            logger.error("Failed to start CLI process: %s", e)
            self.process = None
            return False

    def stop(self) -> None:
        """CLIプロセスを停止する（SIGTERM → タイムアウト後 SIGKILL）。"""
        if self.process is None:
            return

        try:
            if self.process.isalive():
                self.process.terminate(force=False)
                try:
                    self.process.wait()
                except pexpect.TIMEOUT:
                    logger.warning("Process did not terminate, sending SIGKILL")
                    self.process.terminate(force=True)
            self.process.close()
        except Exception as e:
            logger.error("Error stopping CLI process: %s", e)
        finally:
            self.process = None
            logger.info("CLI process stopped")

    async def write(self, data: str) -> None:
        """stdinにデータを書き込む（run_in_executorでブロッキング回避）。"""
        if not self.is_alive:
            return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.process.send, data)

    async def read_output(self, queue: asyncio.Queue) -> None:
        """stdoutを非同期で読み取り、Queueに出力を追加する。"""
        loop = asyncio.get_event_loop()
        while self.is_alive:
            try:
                data = await loop.run_in_executor(
                    None, lambda: self.process.read_nonblocking(size=4096, timeout=0.1)
                )
                if data:
                    await queue.put(data)
            except pexpect.TIMEOUT:
                await asyncio.sleep(0.05)
            except pexpect.EOF:
                logger.info("CLI process EOF")
                break
            except Exception as e:
                logger.error("Error reading output: %s", e)
                break

    def resize(self, cols: int, rows: int) -> None:
        """ターミナルサイズを変更する。"""
        if self.is_alive:
            self.process.setwinsize(rows, cols)
