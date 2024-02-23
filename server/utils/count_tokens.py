"""
Get the number of tokens in a string. for a given encoding. 

See: https://stackoverflow.com/questions/75804599/openai-api-how-do-i-count-tokens-before-i-send-an-api-request
"""

import tiktoken

def num_tokens_from_string(string: str, model_name: str) -> int:
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))

    return num_tokens

# def main():
#     print(num_tokens_from_string("Hello world, let's test tiktoken.", "gpt-3.5-turbo"))
#     print(num_tokens_from_string("Hello world, let's test tiktoken.", "gpt-4"))

# if __name__ == '__main__':
#     main()