from pathlib import Path


class AppTemplateProcessor:
    def replace_app_name(self, directory: Path, components: str) -> None:
        app = components[-1]
        parent = components[-2] if len(components) > 1 else app
        module = '.'.join(components)

        for path in directory.rglob('*'):
            if path.is_file():
                self.replace_content(path, app, parent, module)
                self.rename_file(path, app, parent, module)

    def replace_content(self, path: Path, app: str, parent: str, module: str) -> None:
        replacements = self.generate_replacement(app, parent, module)

        with open(path, 'r', encoding='utf-8') as handle:
            content = handle.read()

        updated_content = self.apply_replacement(content, replacements)

        with open(path, 'w', encoding='utf-8') as file:
            file.write(updated_content)

    def rename_file(self, path: Path, app: str, parent: str, module: str) -> None:
        replacements = self.generate_replacement(app, parent, module)
        new_name = self.apply_replacement(path.name, replacements)

        if new_name != path.name:
            new_path = path.parent / new_name
            path.rename(new_path)

    @staticmethod
    def generate_replacement(
        app: str,
        parent: str,
        module: str
    ) -> dict[str, str]:
        return {
            'module': module,
            'spirepermission': parent.lower() + app.lower(),
            'SpireChildApp': app.capitalize(),
            'SpireChildApps': app.capitalize() + 's',
            'spirechildapp': app.lower(),
            'spirechildapps': app.lower() + 's',
            'SpireParentApp': parent.capitalize(),
            'SpireParentApps': parent.capitalize() + 's',
            'spireparentapp': parent.lower(),
            'spireparentapps': parent.lower() + 's'
        }

    @staticmethod
    def apply_replacement(text: str, replacements: dict[str, str]) -> str:
        for old, new in replacements.items():
            text = text.replace(old, new)

        return text


class HTMLTemplateProcessor:
    def replace_template_names(self, directory: Path, components: list[str]) -> None:
        app = components[-1]
        parent = components[-2] if len(components) > 1 else app
        module = '.'.join(components)

        for path in directory.rglob('*.html'):
            self.replace_content(path, app, parent, module)
            self.rename_file(path, app, parent, module)

    def replace_content(self, path: Path, app: str, parent: str, module: str) -> None:
        replacements = self.generate_replacement(app, parent, module)

        with open(path, 'r', encoding='utf-8') as handle:
            content = handle.read()

        updated_content = self.apply_replacement(content, replacements)

        with open(path, 'w', encoding='utf-8') as file:
            file.write(updated_content)

    def rename_file(self, path: Path, app: str, parent: str, module: str) -> None:
        replacements = self.generate_replacement(app, parent, module)
        new_name = self.apply_replacement(path.name, replacements)

        if new_name != path.name:
            new_path = path.parent / new_name
            path.rename(new_path)

    @staticmethod
    def generate_replacement(app: str, parent: str, module: str) -> dict[str, str]:
        return {
            'module': module,
            'spirepermission': parent.lower() + app.lower(),
            'SpireChildApp': app.capitalize(),
            'SpireChildApps': app.capitalize() + 's',
            'spirechildapp': app.lower(),
            'spirechildapps': app.lower() + 's',
            'SpireParentApp': parent.capitalize(),
            'SpireParentApps': parent.capitalize() + 's',
            'spireparentapp': parent.lower(),
            'spireparentapps': parent.lower() + 's'
        }

    @staticmethod
    def apply_replacement(text: str, replacements: dict[str, str]) -> str:
        for old, new in replacements.items():
            text = text.replace(old, new)

        return text
