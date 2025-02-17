from typing import IO, Callable

FnReadText = Callable[[IO[str]], None]
FnReadBinary = Callable[[IO[bytes]], None]

class FileProcessError(Exception):
    pass
