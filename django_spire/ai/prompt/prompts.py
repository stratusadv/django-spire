from pathlib import Path

from dandy.llm import Prompt


_RELATIVE_BASE_DIR = Path(Path(__file__).parent.parent.parent.parent.resolve())
dandy_prompting_path = Path(_RELATIVE_BASE_DIR, '.venv/Lib/site-packages/dandy/llm/prompt/prompt.py')
dandy_tutorial_path = Path(_RELATIVE_BASE_DIR, 'django_spire/ai/prompt/docs/prompt_tutorial.md')

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

def text_to_markdown_instruction_bot_prompt():
    return (
        Prompt()
        .heading('Markdown Conversion Expert')
        .text('You are an expert in converting plain text into well-formatted Markdown. Your task is to analyze user-provided text and convert it into proper Markdown format, while preserving all original content and enhancing its presentation.')
        .line_break()

        .heading('Goal')
        .text('Convert the user\'s plain text into properly formatted Markdown with appropriate headings, bold text, italics, and other formatting elements.')
        .line_break()

        .heading('Rules and Best Practices')
        .ordered_list([
            'Preserve All Content: Include every word and character from the original text',
            'Infer Structure: Identify headings, lists, emphasis, and other structural elements from context',
            'Apply Proper Markdown: Use standard Markdown syntax (# for headings, ** for bold, * for italics, etc.)',
            'Maintain Hierarchy: Ensure proper heading levels (h1, h2, h3, etc.) based on content hierarchy',
            'Format Lists: Convert bullet points and numbered lists to proper Markdown list format',
            'Enhance Readability: Add appropriate line breaks and spacing for better readability',
            'Preserve Emphasis: Convert emphasized text (ALL CAPS, underlined, etc.) to appropriate Markdown formatting',
            'Add Code Formatting: Identify and properly format code snippets or technical terms',
            'Create Links: Convert URLs to proper Markdown link format',
            'Table Formatting: Convert tabular data into Markdown tables when appropriate'
        ])
        .line_break()

        .heading('Output Format')
        .text('Return the converted Markdown content and a suitable filename with .md extension.')
    )

def dandy_prompt_python_file_input_prompt(user_prompt: str):
    return (
        Prompt()
        .heading('User Prompt:')
        .text(user_prompt)
    )

def text_to_markdown_input_prompt(user_text: str):
    return (
        Prompt()
        .heading('User Text for Markdown Conversion:')
        .text(user_text)
    )
