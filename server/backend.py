"""
Backend methods for handling requests from the frontend
"""

# core imports
import os
import signal

# flask imports
from flask import request

# local imports
from server.langchain.models_info import models
from server.langchain.response_stream import put_prompt_to_queue, sse
from server.conversation.conversation_loader import get_current_conversation_data, get_memory

def get_index_data():
    conversation_id, model, model_parameters, documents, prompt_template = get_current_conversation_data()

    memory = get_memory()

    return {
        'model': model, # current model
        'models': models,
        'memory': memory,
        'documents': documents, # current documents
        'model_parameters': model_parameters,
        'conversation_id': conversation_id,
        'prompt_template': prompt_template, # current prompt template
    }

def chat_response():
    data = request.get_json()

    prompt = data.get('prompt', None)

    if prompt is None:
        raise Exception('prompt is required')
    
    put_prompt_to_queue(prompt)

    return {'success': True}

def sse_response():
    return sse()

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')

    if func is None:
        # fallback to os kill
        os.kill(os.getpid(), signal.SIGINT)

    func()