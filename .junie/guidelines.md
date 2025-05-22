# Django Spire Project Guidelines

## Project Overview
Django Spire is a framework that extends Django to make application development more modular, extensible, and configurable. It provides various components for building web applications, with a focus on portals and CMMS (Computerized Maintenance Management System) functionality.

## Project Structure
- **django_spire/**: Main package containing all the modular components
  - **ai/**: AI functionality including chat components
  - **auth/**: Authentication module
  - **comment/**: Comment functionality
  - **contrib/**: Contributions or additional features
  - **core/**: Core functionality
  - **file/**: File handling
  - **history/**: History tracking
  - **notification/**: Notification system
- **test_project/**: Django project for testing and development
- **docs/**: Documentation files

## Testing Requirements
- Tests should be written for all new functionality
- Tests are organized in app-specific `tests` directories
- Run tests using Django's test framework with the following command:
  ```
  python manage.py test django_spire
  ```
- Tests should maintain the existing test structure and follow Django's testing conventions
- The project uses code coverage tools to ensure adequate test coverage

## Code Style
- Python 3.11 is the target version
- Line length limit is 88 characters
- Use 4 spaces for indentation
- The project uses Ruff for linting with specific rules defined in `ruff.toml`
- Maximum complexity of 10 for functions/methods
- Run linting checks before submitting changes

## Development Environment
- The project includes a development tool (`dev_tool.exe`) for local development
- Docker configuration is available for containerized development
- Python 3.11 or higher is required
- Install dependencies using the requirements files:
  ```
  pip install -r requirements.txt
  ```

## Submission Guidelines
- Ensure all tests pass before submitting changes
- Make sure code follows the style guidelines
- Provide clear commit messages describing the changes
- Update documentation if necessary
