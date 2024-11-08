import argparse
import os
import socket
import subprocess
import sys
import threading

from pathlib import Path
from example.settings import BASE_DIR


if sys.platform == 'win32':
    VENV = Path('.venv') / 'Scripts' / 'python'
else:
    VENV = Path('.venv') / 'bin' / 'python'


def create_superuser() -> None:
    print('Creating superuser...')

    django_superuser_email = os.getenv('DJANGO_SUPERUSER_EMAIL')
    django_superuser_username = os.getenv('DJANGO_SUPERUSER_USERNAME')

    command = [
        VENV,
        'example/manage.py',
        'createsuperuser',
        '--noinput',
        '--email', django_superuser_email,
        '--username', django_superuser_username
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exception:
        print(f"Error creating superuser: {exception}")


def load_secret(path: Path | str = '.env') -> None:
    path = Path(path)

    if not path.exists():
        message = f"The .env file at '{path}' was not found."
        raise FileNotFoundError(message)

    with open(path, 'r', encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()

            if line and not line.startswith('#'):
                key, value = line.split('=', 1)

                key = key.strip()
                value = value.strip()

                os.environ[key] = value.strip()


def set_environment_variables(environment: str = 'local') -> None:
    if not environment:
        message = 'Please enter an environment type.'
        raise ValueError(message)

    if environment == 'local':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'example.settings'

    if environment == 'server':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'example.settings'

    sys.path.append(BASE_DIR)

    load_secret('.env')


def setup_virtual_environment() -> None:
    print('Setting up virtual environment...')

    command = [
        'python',
        '-m',
        'venv',
        '.venv'
    ]

    subprocess.run(command, check=True)

    print('Upgrading pip...')

    command = [
        VENV,
        '-m',
        'pip',
        'install',
        '--upgrade',
        'pip'
    ]

    subprocess.run(command, check=True)

    print('Installing dependencies...')

    command = [
        VENV,
        '-m',
        'pip',
        'install',
        '-U',
        '-r',
        'requirements.txt'
    ]

    subprocess.run(command, check=True)


def start_server(is_migration: str, is_run: str) -> None:
    if is_migration:
        print('Resetting migrations...')

        command = [
            VENV,
            'example/manage.py',
            'spire_remove_migration'
        ]

        subprocess.run(command, check=True)

        print('Making migrations...')

        command = [
            VENV,
            'example/manage.py',
            'makemigrations'
        ]

        subprocess.run(command, check=True)

        print('Applying migrations...')

        command = [
            VENV,
            'example/manage.py',
            'migrate'
        ]

        subprocess.run(command, check=True)

    if is_run:
        print('Running server...')

        command = [
            VENV,
            'example/manage.py',
            'runserver',
            '0.0.0.0:8000',
        ]

        try:
            host = socket.gethostname()
            ip = socket.gethostbyname(host)

            env = os.environ.copy()

            process = subprocess.Popen(
                command,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            def stream_output(process: subprocess.Popen) -> None:
                for line in iter(process.stdout.readline, ''):
                    if 'Starting development server' in line:
                        line = (
                            f"Starting development server at http://127.0.0.1:8000/ "
                            f"or http://{ip}:8000/\n"
                        )

                    print(line, end='')

            thread = threading.Thread(
                target=stream_output,
                args=(process,)
            )

            thread.start()
            process.wait()
            thread.join()

        except subprocess.CalledProcessError as exception:
            message = f"Subprocess failed with error: {exception}"
            print(message)
        except KeyboardInterrupt:
            message = 'Interrupted. Stopping...'
            process.terminate()
            print(message)
            process.wait()


def main() -> None:
    os.environ.setdefault(
        'PYTHONPATH',
        str(BASE_DIR)
    )

    parser = argparse.ArgumentParser(description='Setup and run Django server.')
    parser.add_argument('-e', '--environment', help='Determine which environment to use (e.g., local or server)')
    parser.add_argument('-m', '--migrate', action='store_true', help='Run the migration(s)')
    parser.add_argument('-r', '--run', action='store_true', help='Run the Django server')
    parser.add_argument('-s', '--setup', action='store_true', help='Setup virtual environment and install dependencies')
    parser.add_argument('-su', '--superuser', action='store_true', help='Create a Django superuser')

    args = parser.parse_args()

    if args.setup:
        setup_virtual_environment()

    if args.environment:
        set_environment_variables(args.environment)
    else:
        set_environment_variables()

    if args.superuser:
        create_superuser()

    if args.migrate or args.run:
        start_server(args.migrate, args.run)


if __name__ == '__main__':
    main()
