import os

from pathlib import Path


ALLOW_RECORDING_TO_FILE = True
BASE_PATH = Path.resolve(Path(__file__)).parent.parent


LLM_CONFIGS = {
    'DEFAULT': {
        'TYPE': 'openai',
        'HOST': os.getenv('AI_API_HOST'),
        'PORT': 443,
        'API_KEY': os.getenv('AI_API_KEY'),
        'MODEL': 'stratus.turbo',
        'MAX_INPUT_TOKENS': 32000,
        'MAX_OUTPUT_TOKENS': 32000,
    },
}
