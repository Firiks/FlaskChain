"""
Handle vector_db creation for different file formats
"""

# core imports
import os
import torch
import shutil

# langchain imports
from langchain.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader, JSONLoader #TODO: add WebBaseLoader
from langchain.embeddings import HuggingFaceInstructEmbeddings

# local imports
from server.utils.logger import logger
from server.utils.helpers import get_location, is_absolute_path, detect_file_type

chroma_dir = get_location('../chroma')

def get_db_path(conversation_id):
    global chroma_dir

    return os.path.join(chroma_dir, conversation_id)

def db_exists(persist_directory):
    return os.path.exists(persist_directory)

def remove_db(persist_directory):
    global chroma_dir

    if is_absolute_path(persist_directory):
        shutil.rmtree(persist_directory)
    else:
        persist_directory = os.path.join(chroma_dir, persist_directory)

    shutil.rmtree(persist_directory)

def get_openai_embeddings():
    logger.info('Loading OpenAI embeddings...')

    return OpenAIEmbeddings()

def get_huggingface_embeddings():
    logger.info('Loading HuggingFace embeddings...')

    model_kwargs = { 'device': 'cuda' if torch.cuda.is_available() else 'cpu' }
    encode_kwargs = { 'normalize_embeddings': True }

    # return HuggingFaceBgeEmbeddings(model_name='thenlper/gte-base', model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)
    return HuggingFaceInstructEmbeddings(model_name='hkunlp/instructor-xl', model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)

def get_loader(documents_path):
    # detect what documents type are we dealing with
    type = detect_file_type(documents_path)
    loader = None

    if not type:
        logger.error('Failed to detect file type')
        raise Exception('Failed to detect file type')

    if type == 'pdf':
        loader = DirectoryLoader(documents_path, glob="./*.pdf", loader_cls=PyPDFLoader, show_progress=True)
    elif type == 'txt':
        loader = DirectoryLoader(documents_path, glob="./*.txt", loader_cls=TextLoader, show_progress=True, loader_kwargs={'autodetect_encoding': True})
    elif type == 'json':
        loader = DirectoryLoader(documents_path, glob="*.json", loader_cls=JSONLoader, loader_kwargs={ 'jq_schema': '.', 'text_content': False, 'autodetect_encoding': True }, show_progress=True)
    else:
        logger.error('Unsupported file type')
        raise Exception('Unsupported file type')

    return loader

def make_db_from_documents(documents_path, persist_directory, chunk_size=2000, chunk_overlap=200):
    global chroma_dir

    loader = get_loader(documents_path)
    
    documents = loader.load()

    #splitting the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, # determines the size of each chunk (characters)
        chunk_overlap=chunk_overlap # last X characters of each chunk will be the first X of the next chunk, its used to keep the context
    )

    texts = text_splitter.split_documents(documents)

    logger.info('Loading embeddings...')

    embeddings = get_huggingface_embeddings()

    # embeddings = get_openai_embeddings()

    persist_directory = os.path.join(chroma_dir, persist_directory)

    logger.info('Creating vector database...')

    vector_db = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    vector_db.persist()
    vector_db = None

    return persist_directory

def load_vector_db_from_disk(persist_directory):
    global chroma_dir

    embeddings = get_huggingface_embeddings()

    # embeddings = get_openai_embeddings()

    persist_directory = os.path.join(chroma_dir, persist_directory)

    logger.info('Loading vector database...')

    # Now we can load the persisted database from disk, and use it as normal.
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )