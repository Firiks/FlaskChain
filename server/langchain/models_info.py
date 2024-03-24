"""
Keep track of models and their info.
"""

import json

from server.utils.helpers import get_location

json_path = get_location('../langchain/data/models.json')

models = json.load(open(json_path, 'r'))

def list_models():
    global models

    print('Available models:')

    for model in models:
        print(model['name'])