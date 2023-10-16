import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] - %(filename)s - %(funcName)s - %(message)s',
    encoding='utf-8'
)

log = logging.getLogger('root')


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
