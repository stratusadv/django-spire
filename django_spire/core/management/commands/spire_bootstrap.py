import shutil
import django_spire

from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


INDENT = '    '


class AppManager:
    def __init__(self, base: Path, template: Path):
        self.base = base
        self.template = template

    def get_valid_root_apps(self) -> set[str]:
        return {
            app.split('.')[0]
            for app in settings.INSTALLED_APPS
            if '.' in app and app.split('.')[0] != 'django'
        }

    def validate_root_apps(self, components: list[str]):
        valid = self.get_valid_root_apps()
        root = components[0]

        if root not in valid:
            message = (
                f'Invalid root app "{root}". '
                f'The following are valid root apps: {", ".join(valid)}.'
            )

            raise CommandError(message)

    def validate_app_name_format(self, app: str):
        if '.' not in app:
            message = (
                'Invalid app name format. '
                'The app path must use dot notation (e.g., "parent.child").'
            )

            raise CommandError(message)

    def parse_app_name(self, app: str) -> list[str]:
        return app.split('.') if '.' in app else [app]

    def get_missing_components(
        self,
        components: list[str],
        registered_apps: list[str]
    ) -> list[str]:
        missing = []

        total = len(components)

        for i in range(total):
            app = '.'.join(components[: i + 1])

            if app not in registered_apps and i > 0:
                missing.append(app)

        return missing

    def create_custom_app(
        self,
        app: str,
        processor: 'TemplateProcessor',
        reporter: 'Reporter'
    ):
        components = app.split('.')
        destination = self.base.joinpath(*components)

        if destination.exists():
            reporter.report_app_exists(app, destination)
            return

        reporter.report_creating_app(app, destination)
        destination.mkdir(parents=True, exist_ok=True)

        if not self.template.exists():
            message = (
                f'Template directory "{self.template}" is missing. '
                'Ensure you have a valid app template.'
            )

            raise CommandError(message)

        shutil.copytree(
            self.template,
            destination,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns('__pycache__', '*.pyc')
        )

        processor.replace_app_name(destination, components[-1])
        reporter.report_app_creation_success(app)


class TemplateProcessor:
    def replace_app_name(self, directory: Path, app: str):
        components = app.split('.')
        parent = components[0] if len(components) > 1 else app

        for path in directory.rglob('*'):
            if path.is_file():
                self.replace_content(path, components[-1], parent)
                self.rename_file(path, components[-1], parent)

    def replace_content(self, path: Path, app: str, parent: str):
        replacements = self.generate_replacement(app, parent)

        with open(path, 'r', encoding='utf-8') as handle:
            content = handle.read()

        updated_content = self.apply_replacement(content, replacements)

        with open(path, 'w', encoding='utf-8') as file:
            file.write(updated_content)

    def rename_file(self, path: Path, app: str, parent: str):
        replacements = self.generate_replacement(app, parent)
        new_name = self.apply_replacement(path.name, replacements)

        if new_name != path.name:
            new_path = path.parent / new_name
            path.rename(new_path)

    @staticmethod
    def generate_replacement(app: str, parent: str) -> dict[str, str]:
        return {
            'Placeholder': app.capitalize(),
            'Placeholders': app.capitalize() + 's',
            'placeholder': app.lower(),
            'placeholders': app.lower() + 's',
            'Parent': parent.capitalize(),
            'Parents': parent.capitalize() + 's',
            'parent': parent.lower(),
            'parents': parent.lower() + 's',
        }

    @staticmethod
    def apply_replacement(text: str, replacements: dict[str, str]) -> str:
        for old, new in replacements.items():
            text = text.replace(old, new)

        return text


class Reporter:
    def __init__(self, command: BaseCommand):
        self.command = command

    def report_missing_components(self, missing_components: list[str]):
        self.command.stdout.write(self.command.style.WARNING('The following are not registered apps:'))
        self.command.stdout.write('\n'.join(f' - {app}' for app in missing_components))

    def report_installed_apps_suggestion(self, missing_components: list[str]):
        self.command.stdout.write(self.command.style.NOTICE('\nPlease add the following to INSTALLED_APPS in settings.py:'))
        self.command.stdout.write('\n'.join(f'"{app}"' for app in missing_components))

    def report_app_creation_success(self, app: str):
        self.command.stdout.write(self.command.style.SUCCESS(f'Successfully created app: {app}'))

    def report_app_exists(self, app: str, destination: Path):
        self.command.stdout.write(self.command.style.WARNING(f'App "{app}" already exists at {destination}'))

    def report_creating_app(self, app: str, destination: Path):
        self.command.stdout.write(self.command.style.NOTICE(f'Creating app "{app}" at {destination}'))

    def report_tree_structure(self, base: Path, components: list[str], registered_apps: list[str], template: Path):
        self.command.stdout.write('\nThe following app(s) will be created:\n\n')

        current = base

        for i, component in enumerate(components):
            current = current / component

            app = '.'.join(components[: i + 1])
            indent = INDENT * i

            self.command.stdout.write(f'{indent}📂 {component}/')

            if app not in registered_apps and template.exists():
                self.show_tree_from_template(template, indent=indent + INDENT)

    def prompt_for_confirmation(self, message: str) -> bool:
        return input(message).strip().lower() == 'y'

    def show_tree_from_template(self, template_dir: Path, indent: str = ''):
        ignore = {'__init__.py', '__pycache__'}

        items = sorted(
            template_dir.iterdir(),
            key=lambda p: (p.is_file(), p.name.lower())
        )

        for item in items:
            if item.name in ignore:
                continue

            self.command.stdout.write(f'{indent}{"📁" if item.is_dir() else "📄"} {item.name}')

            if item.is_dir():
                self.show_tree_from_template(item, indent=indent + INDENT)


class Command(BaseCommand):
    help = 'Create a custom Spire app.'

    def __init__(self):
        super().__init__()

        self.base = Path(settings.BASE_DIR)
        self.template = Path(django_spire.__file__).parent / 'template/app'

        self.manager = AppManager(self.base, self.template)
        self.processor = TemplateProcessor()
        self.reporter = Reporter(self)

    def add_arguments(self, parser):
        parser.add_argument(
            'app_name',
            help='The name of the application to create',
            type=str
        )

    def get_app_names(self) -> list[str]:
        from django.apps import apps
        return [config.name for config in apps.get_app_configs()]

    def handle(self, *_args, **kwargs):
        app = kwargs.get('app_name')

        if not app:
            raise CommandError(self.style.ERROR('The app name is missing'))

        self.manager.validate_app_name_format(app)

        components = self.manager.parse_app_name(app)
        self.manager.validate_root_apps(components)

        registered_apps = self.get_app_names()

        self.stdout.write(self.style.NOTICE(f'Checking app components: {components}\n\n'))

        missing_components = self.manager.get_missing_components(components, registered_apps)

        if missing_components:
            self.reporter.report_missing_components(missing_components)
            self.reporter.report_tree_structure(self.base, components, registered_apps, self.template)
            self.reporter.report_installed_apps_suggestion(missing_components)

            if not self.reporter.prompt_for_confirmation('\nProceed with app creation? (y/n): '):
                self.stdout.write(self.style.ERROR('App creation aborted.'))
                return

            for module in missing_components:
                self.manager.create_custom_app(module, self.processor, self.reporter)
        else:
            self.stdout.write(self.style.SUCCESS('All components exist!'))
