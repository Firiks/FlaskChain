"""
Handles the command line interface for the server
"""

import argparse

from server.langchain.models_info import list_models, add_local_model, remove_local_model
from server.conversation.conversation_loader import list_conversations

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run the FlaskChain app, use -i to load existing conversation or -m and -p to start a new one')
    parser.add_argument('-i', '--conversation-id', default='', dest='conversation_id', type=str, help='Conversation ID')
    parser.add_argument('-m', '--model', type=str, default='', help='Name of the model')
    parser.add_argument('-p' ,'--promt-template', dest='prompt_template', default='', type=str, help='Prompt template name')
    parser.add_argument('-t', '--temperature', type=float, default=0.0, help='Temperature for the llm')
    parser.add_argument('-tp', '--top-p', type=float, default=1, dest='top_p', help='Top p for the llm')
    parser.add_argument('-mt', '--max-tokens', type=int, default=4096, dest='max_tokens', help='Max tokens for the llm')
    parser.add_argument('-n', '--n', type=int, default=1, dest='n', help='Number of completions for the llm')
    parser.add_argument('-nc', '--n-ctx', type=int, default=32000, dest='n_ctx', help='Number of context tokens for the llm')
    parser.add_argument('-ngl', '--n-gpu-layers', type=int, default=5, dest='n_gpu_layers', help='Number of GPU layers for the llm')
    parser.add_argument('-nb', '--n-batch', type=int, default=100, dest='n_batch', help='Number of batches for the llm')
    parser.add_argument('-d', '--documents', type=str, default='', help='Path to folder with documents, use absolute path')
    parser.add_argument('-lc', '--list-conversations', dest='list_conversations', default=False, action='store_true', help='List existing conversations')
    parser.add_argument('-lm', '--list-models', dest='list_models', default=False, action='store_true', help='List available models')
    parser.add_argument('-am', '--add-local-model', dest='add_local_model', default='', type=str, help='Name of new local model')
    parser.add_argument('-mp', '--model-path', dest='model_path', default='', type=str, help='Path to local model')
    parser.add_argument('-rm', '--remove-model', dest='remove_model', default='', type=str, help='Name of model to remove')
    # parser.add_argument('-w', '--web', type=str, default='', help='Link to website that will be used for scraping') #TODO: Implement web scraping
    # parser.add_argument('-r', '--repository', type=str, default='', help='Path to repository, use absolute path') #TODO: Implement repository

    return parser.parse_args()

def cli_callbacks(args):
    if args.list_models:
        list_models()
        exit(0)

    if args.remove_model:
        remove_local_model(args.remove_model)
        exit(0)

    if args.add_local_model:
        add_local_model(args.add_local_model, args.model_path)
        exit(0)

    if args.list_conversations:
        list_conversations()
        exit(0)