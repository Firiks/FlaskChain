"""
Conversation module
"""

# core imports
import json

# local imports
from server.db.db import db
from server.utils.logger import logger
from server.langchain.models_info import models
from server.db.models.conversation import Conversation
from server.langchain.prompt_templates import templates
from server.utils.helpers import generate_random_string
from server.langchain.vector_db import make_db_from_documents, get_db_path
from server.langchain.init_llm import init_chain_with_documents, init_standard_chain, init_openai_llm, init_local_llm, load_saved_memory, extract_memory_from_chain

# current conversation global variables
app = None
model = None
memory = None
documents = None
temperature = None
conversation_id = None
prompt_template = None

def set_app(app_instance):
    global app

    app = app_instance

def get_memory():
    global documents

    memory = extract_memory_from_chain(documents)
    memory = json.dumps(memory) if memory else None

    return memory

def get_current_conversation_data():
    global conversation_id, model, temperature, documents, prompt_template

    return conversation_id, model, temperature, documents, prompt_template

def init_llm(model_info, temperature):
    if model_info.get('type') == 'openai':
        init_openai_llm(model_info.get('name'), temperature)
    else:
        init_local_llm(model_info.get('name'), temperature)

def start_conversation(args):
    global conversation_id, model, temperature, documents, prompt_template

    if args.conversation_id:
        conversation_id = args.conversation_id
        load_existing_conversation(conversation_id)
    elif args.model and args.prompt_template:
        model = args.model
        prompt_template = args.prompt_template
        temperature = float(args.temperature if args.temperature else 0.0)
        documents = args.documents

        try:
            model_info = [m for m in models if m['name'] == model][0]
            prompt_template =[t.get('value') for t in templates if t.get('name') == prompt_template][0]
        except:
            logger.error("Invalid model or prompt template")
            exit(1)

        conversation_id = generate_random_string(8)

        logger.info(f"Generated conversation ID: {conversation_id}")

        init_llm(model_info, temperature)
    
        if documents:
            db_path = make_db_from_documents(documents, conversation_id)

            init_chain_with_documents(prompt_template, db_path)
        else:
            init_standard_chain(prompt_template)

        save_or_update_conversation()
    else:
        logger.warning("Please provide either conversation ID or model, prompt template and documents")
        exit(1)

def load_existing_conversation(conversation_id):
    global model, temperature, documents, prompt_template, app

    logger.info(f"Loading conversation with ID {conversation_id}")

    with app.app_context():
        conversation = Conversation.query.filter_by(conversation_id=conversation_id).first()

    if not conversation:
        logger.info(f"Conversation with ID {conversation_id} does not exist")
        exit(1)

    model = conversation.model # model key
    temperature = conversation.temperature # temperature for LLM
    documents = conversation.documents # path to documents
    memory = conversation.memory # serialized memory
    prompt_template = conversation.prompt_template # prompt template

    if memory:
        logger.info(f"Loading memory for conversation with ID {conversation_id}")
        memory = load_saved_memory(json.loads(memory))
    else:
        memory = None

    model_info = [m for m in models if m['name'] == model][0]

    init_llm(model_info, temperature)

    if documents:
        logger.info(f"Documents: {documents}")

        db_path = get_db_path(conversation_id)

        init_chain_with_documents(prompt_template, db_path, memory)
    else:
        init_standard_chain(prompt_template, memory)

def save_or_update_conversation():
    global conversation_id, model, temperature, documents, prompt_template, app, documents

    memory = extract_memory_from_chain(documents)
    memory = json.dumps(memory) if memory else None

    with app.app_context():
        conversation = Conversation.query.filter_by(conversation_id=conversation_id).first()

    if conversation:
        logger.info(f"Updating conversation with ID {conversation_id}")
        conversation.model = model
        conversation.temperature = temperature
        conversation.prompt_template = prompt_template
        conversation.documents = documents
        conversation.memory = memory
    else:
        logger.info(f"Saving new conversation with ID {conversation_id}")
        conversation = Conversation(conversation_id=conversation_id, model=model, temperature=temperature, prompt_template=prompt_template, documents=documents, memory=memory)

    with app.app_context():
        db.session.add(conversation)
        db.session.commit()
