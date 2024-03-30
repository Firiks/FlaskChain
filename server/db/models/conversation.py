"""
Conversation model
"""

from server.db.db import db

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.String(8), unique=True, index=True, nullable=False)
    model = db.Column(db.String(255), nullable=False)
    documents = db.Column(db.String(255), nullable=True)
    model_parameters = db.Column(db.Text, nullable=True) # json
    prompt_template = db.Column(db.Text, nullable=False)
    memory = db.Column(db.Text, nullable=True) # json

    def __init__(self, conversation_id, model, documents, prompt_template, memory=None, model_parameters=None):
        self.conversation_id = conversation_id
        self.model = model
        self.documents = documents
        self.prompt_template = prompt_template
        self.memory = memory
        self.model_parameters = model_parameters

    def __repr__(self):
        return f'<Conversation {self.conversation_id}>'
