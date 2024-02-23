# FlaskChain
RAG and LangChain powered chatbot using Flask

## Description
Chat with remote or local llms(LlamaCpp) using Flask and LangChain. Use documents to enhance llm knowledge using RAG. Store conversation in a database(Sqlite) and retrieve them by id.

## Installation
0. optional - you can create a virtual environment using `python -m venv .venv` and activate it using `source .venv/bin/activate`
1. `pin install -r requirements.txt`
2. `mv .env.example .env` and fill in the required fields
3. `mv start.sh.example start.sh` and `chmod +x start.sh` then use this to init first conversation
4. `mv start-id.sh.example start-id.sh` and `chmod +x start-id.sh` use this to load conversation by id