import os

from pathlib import Path


ALLOW_DEBUG_RECORDING = True
BASE_PATH = Path.resolve(Path(__file__)).parent.parent
DEFAULT_LLM_PROMPT_RETRY_COUNT: int = 2


LLM_CONFIGS = {
    'DEFAULT': {
        'TYPE': 'ollama',
        'HOST': os.getenv('ACTION_OLLAMA_HOST'),
        'PORT': int(os.getenv('OLLAMA_PORT', 11434)),
        'API_KEY': os.getenv('OLLAMA_API_KEY'),
        'MODEL': 'qwen3-coder:30b',
        'TEMPERATURE': 0.1,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'SMART_FAST': {
        'MODEL': 'gemma3:12b',
        'TEMPERATURE': 0.1,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'FAST': {
        'MODEL': 'gemma3:4b',
        'TEMPERATURE': 0.1,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'THINKING': {
        'HOST': os.getenv('THINKING_OLLAMA_HOST'),
        'MODEL': 'qwen3:235b',
        'TEMPERATURE': 0.1,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'SEEDING_LLM_BOT': {
        'TYPE': 'ollama',
        'HOST': os.getenv('ACTION_OLLAMA_HOST'),
        'PORT': int(os.getenv('OLLAMA_PORT', 11434)),
        'API_KEY': os.getenv('OLLAMA_API_KEY'),
        'MODEL': 'qwen3-coder:30b',
        'TEMPERATURE': 0.0,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'PYTHON_MODULE': {
        'TYPE': 'ollama',
        'HOST': os.getenv('ACTION_OLLAMA_HOST'),
        'PORT': int(os.getenv('OLLAMA_PORT', 11434)),
        'API_KEY': os.getenv('OLLAMA_API_KEY'),
        'MODEL': 'qwen3-coder:30b',
        'TEMPERATURE': 0.3,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'QWEN_2_5_CODER_14B': {
        'TYPE': 'ollama',
        'HOST': os.getenv('ACTION_OLLAMA_HOST'),
        'PORT': int(os.getenv('OLLAMA_PORT', 11434)),
        'API_KEY': os.getenv('OLLAMA_API_KEY'),
        'MODEL': 'qwen3-coder:30b',
        'TEMPERATURE': 0.0,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'KNOWLEDGE_LLM_BOT': {
        'TYPE': 'ollama',
        'HOST': os.getenv('ACTION_OLLAMA_HOST'),
        'PORT': int(os.getenv('OLLAMA_PORT', 11434)),
        'API_KEY': os.getenv('OLLAMA_API_KEY'),
        'MODEL': 'qwen3-coder:latest',
        'TEMPERATURE': 0.3,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 32000,
    },
}
