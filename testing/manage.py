import os
import sys

from pathlib import Path


def main() -> None:
    root = str(Path(__file__).resolve().parent.parent)
    sys.path.append(root)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        message = (
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )

        raise ImportError(message) from exc

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
