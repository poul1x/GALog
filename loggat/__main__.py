from logging.config import dictConfig
import yaml

from loggat.app import runApp

if __name__ == "__main__":

    # Configure logging
    with open("logging.yaml") as f:
        dictConfig(yaml.safe_load(f))

    # Run application
    runApp()
