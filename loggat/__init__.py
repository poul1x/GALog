# Registers application resources (images, icons, etc...)
# Resources compiled with: pyrcc5.exe -o ./sqs_gui/app/resources.py ./resources.qrc
from .app import resources

# Explicitly import some dependencies
# to make them fetched by pyinstaller
import coloredlogs
