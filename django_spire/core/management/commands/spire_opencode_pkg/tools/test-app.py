import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import django
from django.core.management import call_command
from io import StringIO

# 1. Define the root directory (the folder that contains the 'system' folder)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_file = BASE_DIR / "development.env"

# 2. Inject the project root into Python's path
sys.path.insert(0, str(BASE_DIR))

# 3. Load environment variables
if env_file.exists():
    load_dotenv(env_file)

# Make sure the settings module is set
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "system.development.settings")

# 4. Initialize Django
django.setup()

if len(sys.argv) < 2:
    print("Error: Please provide an app path")
    print("Usage: python test-app.py <app_path>")
    print("Examples: app.explorer, mort.podcast, app.landing")
    sys.exit(1)

app_path = sys.argv[1]

try:
    print(f"--- Running Tests for: {app_path} ---")
    out = StringIO()
    err = StringIO()

    call_command("test", app_path, stdout=out, stderr=err)

    print(out.getvalue())
    if err.getvalue():
        print(err.getvalue())

except Exception as e:
    print(f"Error running tests: {e}")
    import traceback

    traceback.print_exc()
