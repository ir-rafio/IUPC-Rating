from .baps import BapsParser
from .toph import TophParser
from parser.model import Parser


def get_parser(name: str) -> Parser:
    parsers: dict[str, Parser] = {
        "BAPS": BapsParser(),
        "TOPH": TophParser(),
    }
    try:
        return parsers[name.upper()]
    except KeyError as error:
        raise ValueError(f"Unknown parser: {name}") from error


__all__ = ["Parser", "get_parser"]
