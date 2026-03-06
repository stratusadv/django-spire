import os

from pathlib import Path


ALLOW_RECORDING_TO_FILE = True
BASE_PATH = Path.resolve(Path(__file__)).parent.parent


LLM_CONFIGS = {
    'DEFAULT': {
        'HOST': os.getenv('AI_API_HOST'),
        'PORT': int(os.getenv('AI_API_PORT', '443')),
        'API_KEY': os.getenv('AI_API_KEY'),
        'MODEL': os.getenv('AI_API_MODEL', 'stratus.thinking'),
    },
    'BASIC': {
        'MODEL': 'stratus.smart',
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'ADVANCED': {
        'MODEL': 'stratus.smart',
        'TEMPERATURE': 0.3,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'COMPLEX': {
        'MODEL': 'stratus.smart',
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'SEEDING_LLM_BOT': {
        'MODEL': 'stratus.smart',
        'TEMPERATURE': 0.0,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'PYTHON_MODULE': {
        'MODEL': 'stratus.smart',
        'TEMPERATURE': 0.3,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'QWEN_2_5_CODER_14B': {
        'MODEL': 'stratus.smart',
        'TEMPERATURE': 0.0,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 16000,
    },
    'KNOWLEDGE_LLM_BOT': {
        'MODEL': 'stratus.smart',
        'TEMPERATURE': 0.3,
        'MAX_INPUT_TOKENS': 16000,
        'MAX_OUTPUT_TOKENS': 32000,
    },
}
