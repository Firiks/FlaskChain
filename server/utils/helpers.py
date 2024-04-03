"""
Common helper functions used across the project
"""

import os
import glob
import random
import string
import pprint
import mimetypes

def generate_random_string(length=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def get_location(relative_path):
    current_location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    return os.path.join(current_location, relative_path)

def path_exists(path):
    return os.path.exists(path)

def is_absolute_path(path):
    return os.path.isabs(path)

def create_excerpt_from_text(text, max_length=100):
    if len(text) > max_length:
        return text[:max_length] + '...'

    return text

# TODO: refactor to return tuple of extensions in subdirectory
def detect_file_type(directory_path):
    # Get the first file in the directory
    file_path = next(glob.iglob(f"{directory_path}/*.*"), None)

    if file_path:
        mime, encoding = mimetypes.guess_type(file_path)
        if mime:
            return mime.split('/')[1]  # Extract the second part (subtype) of the MIME type
        else:
            return None
    else:
        return None

def var_dump(var):
    pprint.pprint(var)