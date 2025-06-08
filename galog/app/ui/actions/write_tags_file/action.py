from typing import IO, Iterable

from ..write_file import WriteFileAction


class WriteTagsFileAction(WriteFileAction):
    def _writeTagsFileImpl(self, f: IO[str], tags: Iterable[str]):
        f.write("\n".join(tags))

    def writeTagsFile(self, tags: Iterable[str]):
        self._writeTextData(lambda fd: self._writeTagsFileImpl(fd, tags))
