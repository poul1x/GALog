from typing import Any, Dict
from galog.app.paths import (
    loggingConfigFile,
    appLogsDir,
)
import logging.config
import logging.handlers
import os
import yaml


def updateFileHandlersPaths(config: Dict[str, dict]):
    logsDir = appLogsDir()
    for val in config["handlers"].values():
        configurator = logging.config.BaseConfigurator(config)
        obj = configurator.resolve(val["class"])
        if issubclass(obj, logging.FileHandler):
            val["filename"] = os.path.join(logsDir, val["filename"])


def initLogging():
    loggingConfig = loggingConfigFile()
    with open(loggingConfig, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f.read())

    updateFileHandlersPaths(config)
    logging.config.dictConfig(config)
