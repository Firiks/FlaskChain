"""
Keep track of models and their info.
"""

import os
import json
import openai

from server.utils.logger import logger
from server.utils.helpers import get_location

json_path = get_location('../langchain/data/models.json')

models = json.load(open(json_path, 'r'))

def _sort_models(models_to_sort):
    return sorted(models_to_sort, key=lambda x: x['type'])

def list_models():
    global models

    update_openai_models()

    logger.info('Available models:')

    for model in models:
        logger.info(model['name'])

def update_openai_models():
    global models
    logger.info('Updating OpenAI models...')

    openai.api_key = os.environ['OPENAI_API_KEY']
    openai_models = openai.Model.list()

    # remove existing openai models
    models = [model for model in models if model['type'] != 'openai']

    for model in openai_models['data']:
        logger.info(json.dumps(model, indent=2))

        if 'gpt' in model['id']:
            models.append({'name': model['id'], 'type': 'openai'})

    models = _sort_models(models)

    with open(json_path, 'w') as f:
        json.dump(models, f, indent=2)

def add_local_model(name: str, path: str, type = 'gguf'):
    global models

    name = name.lower().strip()

    # check if model already exists
    for model in models:
        if model['name'] == name:
            logger.info('Model already exists')
            return

    logger.info(f'Adding local model: {name} at {path}')

    models.append({'name': name, 'path': path, 'type': type})

    models = _sort_models(models)

    with open(json_path, 'w') as f:
        json.dump(models, f, indent=2)

def remove_local_model(name: str):
    global models

    name = name.lower().strip()

    logger.info(f'Removing model: {name}')

    models = [model for model in models if model['name'] != name]

    models = _sort_models(models)

    with open(json_path, 'w') as f:
        json.dump(models, f, indent=2)
