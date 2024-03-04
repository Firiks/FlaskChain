"""
Handle the initialization of the LLM and the chain.
"""

# TODO: https://python.langchain.com/docs/expression_language/how_to/message_history

# core imports
import os

from pprint import pprint

# langchain imports
from langchain.chat_models import ChatOpenAI
from langchain.llms.llamacpp import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import RetrievalQA, ConversationChain
from langchain.schema import messages_from_dict, messages_to_dict
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory

# local imports
from server.utils.logger import logger
from server.langchain.vector_db import load_vector_db_from_disk

llm = None
chain = None
retriever = None
vectordb = None

# https://github.com/ShumzZzZz/GPT-Rambling/blob/main/LangChain%20Specific/langchain_add_memory_to_RetrievalQA.ipynb
def extract_memory_from_chain(documents=None):
    global chain

    logger.info("Extracting memory from chain...")

    messages = None

    if documents:
        logger.info(f"Extracting messages from document chain {chain.combine_documents_chain.memory.chat_memory.messages}")

        extracted_messages = chain.combine_documents_chain.memory.chat_memory.messages if chain.combine_documents_chain and chain.combine_documents_chain.memory.chat_memory.messages else []
    else:
        logger.info(f"Extracting messages from regular chain")

        extracted_messages = chain.memory.chat_memory.messages if chain.memory else []

    if extracted_messages:
        pprint(extracted_messages)

        logger.info(f"Extracted messages from chain: {extracted_messages}")

        messages = messages_to_dict(extracted_messages)

    return messages

def load_saved_memory(messages):
    logger.info("Loading saved memory...")

    retrieved_messages = messages_from_dict(messages)

    retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)

    retrieved_memory = ConversationBufferMemory(
        chat_memory=retrieved_chat_history,
        memory_key="history",
        input_key="question"
    )

    return retrieved_memory

def init_local_llm(model_info, temperature=0.0):
    global llm

    model_path = model_info.get('path')

    # verify that the model path exists
    if not os.path.exists(model_path):
        raise Exception(f"Model path {model_path} does not exist")

    #TODO: tweak the parameters
    llm = LlamaCpp(
        model_path=model_path,
        temperature=temperature,
        n_ctx=2048,
        n_gpu_layers=10,
        n_batch=100,
        streaming=True,
        callbacks=[]
    )

    logger.info(f"Local LLM: {model_info.get('name')} has been loaded")

def init_openai_llm(model_name, temperature=0.0):
    global llm

    llm = ChatOpenAI(
        model=model_name,
        temperature=temperature,
        streaming=True,
    )

    logger.info(f"OpenAI LLM: {model_name} has been loaded")

def init_standard_chain(template, memory = None):
    global chain, llm

    prompt_template = PromptTemplate.from_template(template)

    chain = ConversationChain(
        prompt=prompt_template,
        llm=llm,
        verbose=True,
        memory=memory
    )

def init_chain_with_documents(template, persist_directory, memory=None):
    global chain, llm, retriever, vectordb

    if not memory:
        memory = ConversationBufferMemory(
            memory_key="history",
            input_key="question"
        )

    vectordb = load_vector_db_from_disk(persist_directory)

    retriever = vectordb.as_retriever()

    prompt_template = PromptTemplate(
        input_variables=["history", "context", "question"],
        template=template,
    )

    chain_type_kwargs = {
        'verbose': True,
        'prompt': prompt_template,
        'memory': memory,
    }

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type='stuff',
        retriever=retriever,
        return_source_documents=False, # TODO: enable and return as metadata
        verbose=True,
        chain_type_kwargs=chain_type_kwargs,
    )

    logger.info(f"QA chain with documents initialized")

def chain_run(prompt, callbacks):
    global chain

    return chain.run(prompt, callbacks=callbacks)

def destroy_chain():
    global chain, llm, retriever, vectordb

    logger.info("Destroying chain...")

    chain = None
    llm = None
    retriever = None
    vectordb = None