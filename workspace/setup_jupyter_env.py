import os
from pathlib import Path
from dotenv import load_dotenv
import django

from example.settings import BASE_DIR

env_path = Path(BASE_DIR) / 'development.env'
if env_path.exists():
    load_dotenv(env_path)

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

django.setup()
