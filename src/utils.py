import datetime
import io
import json
import os
import random
import time
from datetime import datetime

from PIL import Image

import definitions
from src.decorators import timer

"""
    Utility functions that are used by many cogs and modules.
"""


@DeprecationWarning
def load_settings():
    config_path = os.path.join(definitions.root_dir, 'settings.json')
    with open(config_path) as json_file:
        settings = json.load(json_file)
    return settings


def get_current_time() -> str:
    return datetime.utcfromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")


def find_word(string: str, word: str) -> bool:
    """Looks for a word in string, returns True if found, False if not. Does not return True for words in words,
    when you have motorboat and want to check if orb is in the string, this will return False.

    find_word("moped", "mop")
    >>False
    find_word("I love this bot very much!", "bot")
    >>True
    """
    # Spaces are there to not return words in words.
    return f' {word.lower()} ' in f' {string.lower()} '


def is_me(mentions: "list of mentions") -> bool:
    """Checks whether mentions contain this bot's id."""
    for mention in mentions:
        if mention.id == definitions.bot_id:
            return True


def is_owner(user_id: "user id as integer") -> bool:
    """Checks whether given user_id matches bot owners id. Useful to check before executing critical commands,
    like cog loading. There is a decorator commands.is_owner(), but it won't work if you have a dedicated Discord
    account for bots and use different account for personal use. This solves it.
    """
    return user_id == definitions.sudoer


@DeprecationWarning
def generate_graph_path_filename() -> "path and filename for a temporary file":
    path = os.path.join(definitions.root_dir, definitions.temporary_dir)
    now = str(datetime.now().strftime("%Y%m%d%H%M%S"))
    random_number = random.randint(10000, 100000)
    return os.path.join(path, f"{now}_{random_number}.png")


@DeprecationWarning
def get_database() -> "path to database":
    """Returns database path from config with the right path."""
    return os.path.join(definitions.root_dir, definitions.database)


@timer
def pillow_join_images(images: list, direction='horizontal', bg_color=(255, 255, 255), alignment='center'):
    """Appends images in horizontal/vertical direction.

    https://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-python

    :param images: List of PIL image paths.
    :param direction: Direction of concatenation, 'horizontal' or 'vertical'
    :param bg_color: Background color (default: white)
    :param alignment: alignment mode if images need padding. 'left', 'right', 'top', 'bottom', or 'center'
    :return Concatenated image as a new PIL image object.
    """
    open_images = [Image.open(x) for x in images]
    widths, heights = zip(*(i.size for i in open_images))

    if direction == 'horizontal':
        new_width = sum(widths)
        new_height = max(heights)
    else:
        new_width = max(widths)
        new_height = sum(heights)

    img = Image.new('RGB', (new_width, new_height), color=bg_color)

    offset = 0
    for im in open_images:
        if direction == 'horizontal':
            y = 0
            if alignment == 'center':
                y = int((new_height - im.size[1]) / 2)
            elif alignment == 'bottom':
                y = new_height - im.size[1]
            img.paste(im, (offset, y))
            offset += im.size[0]
        else:
            x = 0
            if alignment == 'center':
                x = int((new_width - im.size[0]) / 2)
            elif alignment == 'right':
                x = new_width - im.size[0]
            img.paste(im, (x, offset))
            offset += im.size[1]

    # Free up memory.
    for x in open_images:
        x.close()
    image_path = io.BytesIO()
    img.save(image_path, format="png")
    image_path.seek(0)
    return image_path


@timer
def pillow_add_margin(image_path: str, top: int, right: int, bottom: int, left: int, color=(255, 255, 255)):
    """Add margins to a given image.

    https://note.nkmk.me/en/python-pillow-add-margin-expand-canvas/
    """
    image = Image.open(image_path)
    width, height = image.size
    new_width = width + right + left
    new_height = height + top + bottom
    img = Image.new(image.mode, (new_width, new_height), color)
    img.paste(image, (left, top))
    img.save(image_path, format="png")
    img.seek(0)
    return image_path


@timer
def pillow_join_grid(t: int = 0, r: int = 0, b: int = 0, l: int = 0, *columns: list) -> "path to image":
    """Given image padding and columns, returns a single path to image.

    Joins multiple columns horizontally. Images in columns are joined vertically.
    Padding is applied to each image before joining.
    """
    joined_columns = []
    # Add padding to each image in column and then send them to be joined vertically.
    for col in columns:
        images_with_margins = []
        for image in col:
            if image: images_with_margins.append(pillow_add_margin(image, t, r, b, l))
        joined_columns.append(pillow_join_images(images_with_margins, direction="vertical"))
    # Join column images horizontally into one image.
    return pillow_join_images(joined_columns)


def shift_hour(hour: str, offset: int) -> str:
    """Given a hour 0-23 and offset, shifts it by that amount.

    23 + 2 -> 1
    2 + 2 -> 4
    """
    hour = int(hour) + offset
    if hour >= 24:
        hour -= 24
    if hour < 0:
        hour += 24
    return str(hour) + ":00"


def sort_weekday(weekday_number: int):
    """Americans start week with Sunday and give it a numerical representation of 0.
    This ruins my day, because week starts on a Monday morning. This function solves it.
    It is a sorting function that you can pass to sorted() and have normal weekday sorting!

    Arguments:
        weekday_number: Integer representation of weekday between 0 and 6

    Returns:
        Weekday integer for Europe, Monday is 1, Sunday is 7.
    """
    days = {
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6,
        "Sunday": 7,
    }
    return days[weekday_number]