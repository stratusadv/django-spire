import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'development.env'))

import django
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

django.setup()
