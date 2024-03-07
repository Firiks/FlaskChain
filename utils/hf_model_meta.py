from huggingface_hub import HfApi

api = HfApi()

def search_model(search: str):
    global api

    models = api.list_models(
        search=search,
    )
    return models
