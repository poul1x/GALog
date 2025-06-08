from PyQt5.QtCore import QMutex, QMutexLocker, QWaitCondition


class Event:
    def __init__(self):
        self._mutex = QMutex()
        self._condition = QWaitCondition()
        self._flag = False

    def set(self):
        with QMutexLocker(self._mutex):
            self._flag = True
            self._condition.wakeAll()

    def clear(self):
        with QMutexLocker(self._mutex):
            self._flag = False

    def wait(self, timeout: int):
        with QMutexLocker(self._mutex):
            if not self._flag:
                self._condition.wait(self._mutex, timeout)

    def is_set(self):
        with QMutexLocker(self._mutex):
            return self._flag

    isSet = is_set