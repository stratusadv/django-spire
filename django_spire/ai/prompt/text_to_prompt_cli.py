from django_spire.ai.prompt.bots import DandyPythonPromptBot

def text_to_prompt_cli():
    prompt = input('Enter your prompt: ')
    DandyPythonPromptBot().process(prompt)
