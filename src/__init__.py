import os
import sys

from src.logger import setup_loggers
from src.bot import start_bot
import definitions


def main():
    print("lil_analytics: Adding src/ to syspath!")
    sys.path.insert(0, os.path.join(definitions.root_dir, "src/"))

    print("lil analytics: Setting up logging.")
    setup_loggers()

    print("lil_analytics: Calling start_bot() in bot.py!")
    start_bot()
