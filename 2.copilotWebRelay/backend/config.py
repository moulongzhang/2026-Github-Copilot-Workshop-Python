import os
from dataclasses import dataclass, field


@dataclass
class Config:
    COPILOT_CMD: str = field(default_factory=lambda: os.environ.get("COPILOT_CMD", "copilot"))
    HOST: str = field(default_factory=lambda: os.environ.get("HOST", "0.0.0.0"))
    PORT: int = field(default_factory=lambda: int(os.environ.get("PORT", "8000")))
    DEFAULT_COLS: int = field(default_factory=lambda: int(os.environ.get("DEFAULT_COLS", "80")))
    DEFAULT_ROWS: int = field(default_factory=lambda: int(os.environ.get("DEFAULT_ROWS", "24")))


config = Config()
