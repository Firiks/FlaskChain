:: https://medium.com/@sasika.roledene/unlocking-llm-running-llama-2-70b-on-a-gpu-with-langchain-561adc616b16
:: https://medium.com/@piyushbatra1999/installing-llama-cpp-python-with-nvidia-gpu-acceleration-on-windows-a-short-guide-0dfac475002d

:: check nvidia cuda compiler
nvcc --version

:: check smi
nvidia-smi

.venv/Scripts/activate.bat

set CMAKE_ARGS = "-DLLAMA_OPENBLAS=on"
set FORCE_CMAKE = 1
pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir