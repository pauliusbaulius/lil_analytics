"""
2020-12-07
Future me and anyone desperate enough to be here:
ROOT_DIR gets the right current path of the BOT files, not where your shell is executing,
otherwise BOT files will not find other modules and nothing will work!

No idea if this is the right way to do it, but it never broke. And I am thanful for that.
"""

import pathlib

ROOT_DIR = pathlib.Path(__file__).parent.resolve()