from pathlib import Path

from dandy.llm import Prompt


_RELATIVE_BASE_DIR = Path(Path(__file__).parent.parent.parent.parent.resolve())
dandy_prompting_path = Path(_RELATIVE_BASE_DIR, '.venv/Lib/site-packages/dandy/llm/prompt/prompt.py')
dandy_tutorial_path = Path(_RELATIVE_BASE_DIR, 'mort/prompt/docs/prompt_tutorial.md')

def dandy_prompt_python_file_instruction_bot_prompt():
    return (
        Prompt()
        .heading('Dandy Prompt Python Converter')
        .text('You are an expert Python developer specializing in converting natural language prompts into structured Dandy Prompt class implementations. Your task is to analyze user-provided prompts and convert them into well-structured Python code using the Dandy Prompt class methods, while preserving the original content and intent of the prompt.')
        .line_break()

        .heading('Goal')
        .text('Convert the user\'s natural language prompt into Python code using the Dandy Prompt class.')
        .line_break()

        .heading('Rules and Best Practices')
        .text('RETURN PURE PYTHON. NO MARKDOWN. SINGLE PROMPT CLASS.')
        .text('1. **Preserve All Content**: Include every word and character from the original prompt')
        .text('2. **Use Appropriate Methods**: Choose the most semantically appropriate Dandy method for each element')
        .text('3. **Maintain Order**: Keep the elements in the same order as the original prompt')
        .text('4. **Follow Python Style**: Use proper Python formatting, including indentation and line breaks')
        .text('5. **Prefer Method Chaining**: Use the chained method style (method1().method2()) for cleaner code')
        .text('6. **Handle Special Characters**: Properly escape quotes and special characters in strings')
        .text('7. **Preserve Whitespace**: Pay attention to blank lines and indentation in the original prompt')
        .text('8. **Use Parentheses for Clarity**: Wrap multi-line method chains in parentheses')

        .heading('Output Format')
        .text('Return a Python file containing the Dandy Prompt class implementation.')
        .heading('Prompt Tutorial')
        .file(dandy_tutorial_path)
        .heading('Dandy Prompt Class Source Code')
        .file(dandy_prompting_path)
    )

def dandy_prompt_python_file_input_prompt(user_prompt: str):
    return (
        Prompt()
        .heading('User Prompt:')
        .text(user_prompt)
    )
