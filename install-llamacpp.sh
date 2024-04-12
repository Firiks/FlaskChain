# pre compiled wheel
source ./.venv/Scripts/activate && pip install llama-cpp-python \
  --force-reinstall --upgrade --no-cache-dir \
  --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu122 # chage cu122 to your cuda version