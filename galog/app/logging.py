from contextlib import suppress
import logging.config
import os
import shutil
from typing import Dict

import yaml
import os

from datetime import datetime, timedelta

from galog.app.paths import appLogsDir, appLogsRootDir, loggingConfigFile


def updateFileHandlersPaths(config: Dict[str, dict]):
    logsDir = appLogsDir()
    for val in config["handlers"].values():
        configurator = logging.config.BaseConfigurator(config)
        obj = configurator.resolve(val["class"])
        if issubclass(obj, logging.FileHandler):
            val["filename"] = os.path.join(logsDir, val["filename"])


def updateLoggersPascalCase(config: Dict[str, dict]):
    def snakeCaseToPascalCase(s: str):
        return "".join(word.capitalize() for word in s.split("_"))

    config["loggers"] = {
        snakeCaseToPascalCase(loggerName): loggerCfg
        for loggerName, loggerCfg in config["loggers"].items()
    }


def _removeOldLogs(lastDate: datetime):
    rootDir = appLogsRootDir()
    for dirName in os.listdir(rootDir):
        logDir = os.path.join(rootDir, dirName)
        dateModified = datetime.fromtimestamp(os.path.getmtime(logDir))

        if dateModified > lastDate:
            continue

        with suppress(Exception):
            shutil.rmtree(logDir)


def initializeLogging():
    loggingConfig = loggingConfigFile()
    with open(loggingConfig, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f.read())

    os.makedirs(appLogsDir(), exist_ok=True)
    _removeOldLogs(datetime.now() - timedelta(days=1))

    updateFileHandlersPaths(config)
    updateLoggersPascalCase(config)
    logging.config.dictConfig(config)
