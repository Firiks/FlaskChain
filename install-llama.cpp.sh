# https://medium.com/@sasika.roledene/unlocking-llm-running-llama-2-70b-on-a-gpu-with-langchain-561adc616b16

source ./.venv/Scripts/activate

set CMAKE_ARGS = "-DLLAMA_OPENBLAS=on"
set FORCE_CMAKE = 1
pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir