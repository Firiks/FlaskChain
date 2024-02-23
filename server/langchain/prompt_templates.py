"""
Templates for llm model
"""

import json

from server.utils.helpers import get_location

json_path = get_location('../langchain/data/prompt_templates.json')

templates = json.load(open(json_path, 'r'))
