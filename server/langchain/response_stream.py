"""
Stream response from langchain to client via SSE
"""

# core imports
import json
import time
import html
import threading
from queue import Queue
from typing import Any, Dict, List
from uuid import UUID

# langchain imports
from langchain.schema.output import LLMResult
from langchain.callbacks.base import BaseCallbackHandler

# local imports
from server.utils.logger import logger
from server.langchain.init_llm import chain_run
from server.conversation.conversation_loader import save_or_update_conversation

sse_thread = None
sse_queue = None
prompt_queue = None

def init_queues():
    global sse_queue, prompt_queue

    sse_queue = Queue()
    prompt_queue = Queue()

def put_prompt_to_queue(prompt):
    global prompt_queue

    prompt_queue.put(prompt)

class StreamHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        global sse_queue

        # message in tokens
        sse_queue.put({'type': 'token', 'content': token})

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        global sse_queue

        # start message
        sse_queue.put({'type': 'start'})

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        global sse_queue

        logger.info(f"Stream ended with response: {response}")

        # end message
        sse_queue.put({'type': 'end'})

    def on_llm_error(self, error: BaseException, **kwargs) -> None:
        global sse_queue

        logger.error(f"Error: {error}")

        # error message
        sse_queue.put({'type': 'error', 'content': str(error)})

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        logger.info(f"Chain ended, saving conversation...")

        save_or_update_conversation()

# see https://blog.stackademic.com/streaming-responses-from-llm-using-langchain-fastapi-329f588d3b40
def sse():
    global sse_thread

    while True:
        if not prompt_queue.empty():
            if sse_thread and sse_thread.is_alive():
                continue

            prompt = prompt_queue.get()

            logger.info(f"Streaming for prompt: {prompt}")

            sse_thread = threading.Thread(target=chain_run, args=(prompt,), kwargs={'callbacks': [StreamHandler()]})
            sse_thread.start()

        while not sse_queue.empty():
            sse_event = sse_queue.get()
            yield f"data: {json.dumps(sse_event)}\n\n"

        time.sleep(1)