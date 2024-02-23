from server.db.db import db

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.String(8), unique=True, index=True, nullable=False)
    model = db.Column(db.String(255), nullable=False)
    documents = db.Column(db.String(255), nullable=True)
    temperature = db.Column(db.Float, nullable=False)
    prompt_template = db.Column(db.String(255), nullable=False)
    memory = db.Column(db.Text, nullable=True)

    def __init__(self, conversation_id, model, documents, temperature, prompt_template, memory=None):
        self.conversation_id = conversation_id
        self.model = model
        self.documents = documents
        self.temperature = temperature
        self.prompt_template = prompt_template
        self.memory = memory

    def __repr__(self):
        return f'<Conversation {self.conversation_id}>'
