import logging
from fastapi import WebSocket
from typing import List
import asyncio

connections: List[WebSocket] = []


class WebSocketHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        for connection in connections:
            asyncio.ensure_future(connection.send_text(log_entry))


class Color:
    RESET = "\033[0m"

    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    HIDDEN = "\033[8m"

    Red = "\033[31m"
    Green = "\033[32m"
    Yellow = "\033[33m"
    Blue = "\033[34m"
    Magenta = "\033[35m"
    Cyan = "\033[36m"
    Gray = "\033[37m"
    White = "\033[47m"


# Create a WebSocket handler
websocket_handler = WebSocketHandler()
websocket_formatter = logging.Formatter('\033[1m%(asctime)s :  %(levelname)s :  \033[0m%(message)s',
                                        datefmt='%Y-%m-%d %H:%M:%S')
websocket_handler.setFormatter(websocket_formatter)

# Create a console handler
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('[%(levelname)s] - %(message)s')
console_handler.setFormatter(console_formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[websocket_handler, console_handler],
    encoding='utf-8'
)

log = logging.getLogger('root')