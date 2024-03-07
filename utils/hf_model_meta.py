"""
Get metadata from Huggingface model hub
"""

from huggingface_hub import HfApi
from huggingface_hub import ModelCard

api = HfApi()

def search_model(search: str, limit: int = 5):
    global api

    models = api.list_models(
        search=search,
        limit=5
    )

    return models

def get_model_card(model_id: str):
    model_card = ModelCard.load(model_id)

    return model_card

if __name__ == "__main__":
    models = search_model("TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF")

    for model in models:
        print(model)

    print(get_model_card("TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF"))