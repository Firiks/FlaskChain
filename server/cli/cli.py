import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run the FlaskChain app, use -i to load existing conversation or -m and -p to start a new one')
    parser.add_argument('-i', '--conversation-id', default='', dest='conversation_id', type=str, help='Conversation ID')
    parser.add_argument('-m', '--model', type=str, default='', help='Name of the model')
    parser.add_argument('-p' ,'--promt-template', dest='prompt_template', default='', type=str, help='Prompt template name')
    parser.add_argument('-t', '--temperature', type=float, default=0.0, help='Temperature for the llm')
    parser.add_argument('-d', '--documents', type=str, default='', help='Path to folder with documents, use absolute path')
    # parser.add_argument('-w', '--web', type=str, default='', help='Link to website that will be used for scraping') #TODO: Implement web scraping
    # parser.add_argument('-r', '--repository', type=str, default='', help='Path to repository, use absolute path') #TODO: Implement repository
  
    return parser.parse_args()