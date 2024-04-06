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
from server.prompts.prompt_template import assemble_template
from server.utils.helpers import generate_random_string, path_exists
from server.langchain.vector_db import make_db_from_documents, get_db_path
from server.langchain.init_llm import init_chain_with_documents, init_standard_chain, init_openai_llm, init_local_llm, load_saved_memory, extract_memory_from_chain, parse_model_parameters

# current conversation global variables
app = None
model = None
memory = None
documents = None
model_type = None
model_parameters = None
conversation_id = None
prompt_template = None

def set_app(app_instance):
    global app

    app = app_instance

def get_memory():
    global documents

    memory = extract_memory_from_chain(documents)

    if not memory:
        memory = []

    return memory

def get_current_conversation_data():
    global conversation_id, model, model_parameters, documents, prompt_template

    return conversation_id, model, model_parameters, documents, prompt_template

def init_llm(model_info, model_parameters):
    if model_info.get('type') == 'openai':
        init_openai_llm(model_info.get('name'), **model_parameters)
    else:
        init_local_llm(model_info, **model_parameters)

def start_conversation(args):
    global conversation_id, model, model_parameters, documents, prompt_template, model_type

    if args.conversation_id:
        conversation_id = args.conversation_id
        load_existing_conversation(conversation_id)
    elif args.model and args.prompt_template:
        model = args.model
        prompt_template_id = args.prompt_template if args.prompt_template else 'base'
        model_parameters = parse_model_parameters(args)
        documents = args.documents

        try:
            # get model info, TODO: check if model exists in huggingface
            model_info = [m for m in models if m['name'] == model][0]

            model_type = model_info.get('type')
            rag = True if documents != '' else False
            derive = args.derive_outside_documents if rag else False
            is_llama = model_type == 'gguf'

            # assemble prompt template
            prompt_template = assemble_template(prompt_template_id, rag, derive, is_llama)
        except Exception as e:
            logger.error(f"Error while starting conversation: {e}")
            exit(1)

        conversation_id = generate_random_string(8)

        logger.info(f"Generated conversation ID: {conversation_id}")

        init_llm(model_info, model_parameters)
    
        if documents != '' and path_exists(documents):
            db_path = make_db_from_documents(documents, conversation_id)

            init_chain_with_documents(prompt_template, db_path)
        else:
            init_standard_chain(prompt_template)

        save_or_update_conversation()
    else:
        logger.warning("Please provide either conversation ID or model, prompt template and documents")
        exit(1)

def load_existing_conversation(conversation_id):
    global model, model_parameters, model_type, documents, prompt_template, app

    logger.info(f"Loading conversation with ID {conversation_id}")

    with app.app_context():
        conversation = Conversation.query.filter_by(conversation_id=conversation_id).first()

    if not conversation:
        logger.info(f"Conversation with ID {conversation_id} does not exist")
        exit(1)

    model = conversation.model # model key
    model_parameters = json.loads(conversation.model_parameters)
    model_type = conversation.model_type
    documents = conversation.documents # path to documents
    memory = conversation.memory # serialized memory
    prompt_template = conversation.prompt_template # prompt template

    if memory:
        logger.info(f"Loading memory for conversation with ID {conversation_id}")
        memory = load_saved_memory(json.loads(memory))
    else:
        memory = None

    model_info = [m for m in models if m['name'] == model][0]

    init_llm(model_info, model_parameters)

    if documents:
        logger.info(f"Documents: {documents}")

        db_path = get_db_path(conversation_id)

        init_chain_with_documents(prompt_template, db_path, memory)
    else:
        init_standard_chain(prompt_template, memory)

def save_or_update_conversation():
    global conversation_id, model, documents, prompt_template, app, documents, model_parameters, model_type

    memory = extract_memory_from_chain(documents)
    memory = json.dumps(memory) if memory else None

    with app.app_context():
        conversation = Conversation.query.filter_by(conversation_id=conversation_id).first()

    if conversation:
        logger.info(f"Updating conversation with ID {conversation_id}")
        conversation.model = model
        conversation.model_type = model_type
        conversation.model_parameters = json.dumps(model_parameters)
        conversation.prompt_template = prompt_template
        conversation.documents = documents
        conversation.memory = memory
    else:
        logger.info(f"Saving new conversation with ID {conversation_id}")
        conversation = Conversation(
            conversation_id=conversation_id,
            model=model, 
            model_type=model_type,
            model_parameters=json.dumps(model_parameters),
            prompt_template=prompt_template,
            documents=documents,
            memory=memory
        )

    with app.app_context():
        db.session.add(conversation)
        db.session.commit()

def manual_conversation_update(c_id, m, mp, pt):
    global app, conversation_id, model, model_parameters, prompt_template

    with app.app_context():
        conversation = Conversation.query.filter_by(conversation_id=c_id).first()

    if conversation:
        conversation.model = m
        conversation.model_parameters = json.dumps(mp)
        conversation.documents = documents
        conversation.prompt_template = pt

        with app.app_context():
            db.session.commit()

    else:
        logger.error(f"Conversation with ID {conversation_id} does not exist")

def list_conversations():
    with app.app_context():
        conversations = Conversation.query.all()

    if conversations:
        for conversation in conversations:
            logger.info(f"Conversation ID: {conversation.conversation_id}, Model: {conversation.model}, Prompt template: {conversation.prompt_template}, Documents: {conversation.documents}")
    else:
        logger.info("No conversations found")