import argparse
import os
import socket
import subprocess
import sys
import threading

from pathlib import Path
from playground.settings import BASE_DIR


if sys.platform == 'win32':
    VENV = Path('venv') / 'Scripts' / 'python'
else:
    VENV = Path('venv') / 'bin' / 'python'


def set_environment_variables(environment: str = 'local') -> None:
    if not environment:
        message = 'Please enter an environment type.'
        raise ValueError(message)

    if environment == 'local':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'playground.settings'

    if environment == 'server':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'playground.settings'

    sys.path.append(BASE_DIR)


def setup_virtual_environment() -> None:
    print('Setting up virtual environment...')

    command = [
        'python',
        '-m',
        'venv',
        'venv'
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
        print('Making migrations...')

        command = [
            VENV,
            'playground/manage.py',
            'makemigrations'
        ]

        subprocess.run(command, check=True)

        print('Applying migrations...')

        command = [
            VENV,
            'playground/manage.py',
            'migrate'
        ]

        subprocess.run(command, check=True)

    if is_run:
        print('Running server...')

        command = [
            VENV,
            'playground/manage.py',
            'runserver',
            '0.0.0.0:8000',
        ]

        try:
            host = socket.gethostname()
            ip = socket.gethostbyname(host)

            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'

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
    parser = argparse.ArgumentParser(description='Setup and run Django server.')
    parser.add_argument('-e', '--environment', help='Determine which environment to use (e.g., local or server)')
    parser.add_argument('-m', '--migrate', action='store_true', help='Run the migration(s)')
    parser.add_argument('-r', '--run', action='store_true', help='Run the Django server')
    parser.add_argument('-s', '--setup', action='store_true', help='Setup virtual environment and install dependencies')

    args = parser.parse_args()

    if args.setup:
        setup_virtual_environment()

    if args.environment:
        set_environment_variables(args.environment)
    else:
        set_environment_variables()

    if args.migrate or args.run:
        start_server(args.migrate, args.run)


if __name__ == '__main__':
    main()
