"""
Handle the initialization of the LLM and the chain.
"""

# core imports
import os

# langchain imports
from langchain.chat_models import ChatOpenAI
from langchain.llms.llamacpp import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import RetrievalQA, ConversationChain, LLMChain
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
        logger.info(f"Extracted messages from chain: {extracted_messages}")

        messages = messages_to_dict(extracted_messages)

    return messages

# TODO: token counting llama & openai
# def get_token_count(text, type):
#     global llm

#     if type == 'gguf':
#         return llm.get_num_tokens(text)
#     elif type == 'openai':
#         # count openai tokens
#         pass

def parse_model_parameters(model_parameters, type='gguf'):
    model_parameters = vars(model_parameters)

    if type == 'gguf':
        parsed_params = {
            'temperature': float(model_parameters.get('temperature', 0.0)),
            'top_p': float(model_parameters.get('top_p', 0.95)),
            'top_k': int(model_parameters.get('top_k', 40)),
            'repeat_penalty': float(model_parameters.get('repeat_penalty', 1.1)),
            'max_tokens': int(model_parameters.get('max_tokens', 4096)),
            'n_ctx': int(model_parameters.get('n_ctx', 32000)),
            'n_gpu_layers': int(model_parameters.get('n_gpu_layers', 5)),
            'n_batch': int(model_parameters.get('n_batch', 512)),
        }
    elif type == 'openai':
        parsed_params = {
            'temperature': float(model_parameters.get('temperature', 0.0)),
            'max_tokens': int(model_parameters.get('max_tokens', 4096)),
            'n': int(model_parameters.get('n', 1)),
        }

    return parsed_params

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

def init_local_llm(model_info, temperature, top_p, top_k, max_tokens, n_ctx, n_gpu_layers, n_batch, repeat_penalty):
    global llm

    model_path = model_info.get('path')

    # verify that the model path exists
    if not os.path.exists(model_path):
        raise Exception(f"Model path {model_path} does not exist")

    llm = LlamaCpp(
        # n_threads=8,
        model_path=model_path,
        top_p=top_p,
        top_k=top_k,
        repeat_penalty= repeat_penalty,
        temperature=temperature,
        n_ctx=n_ctx,
        max_tokens=max_tokens,
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        streaming=True,
        f16_kv=True, # MUST set to True, otherwise you will run into problem after a couple of calls
        callbacks=[],
    )

    logger.info(f"Local LLM: {model_info.get('name')} has been loaded")

def init_openai_llm(model_name, temperature, max_tokens, n):
    global llm

    llm = ChatOpenAI(
        model=model_name,
        max_tokens=max_tokens,
        temperature=temperature,
        model_kwargs={
            'n': n
        },
        streaming=True,
    )

    logger.info(f"OpenAI LLM: {model_name} has been loaded")

def init_standard_chain(template, memory = None):
    global chain, llm

    prompt_template = PromptTemplate.from_template(template)

    chain = LLMChain(
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