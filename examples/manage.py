import os
import sys

from settings import BASE_DIR


def main() -> None:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examples.settings')
    sys.path.append(BASE_DIR)

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
