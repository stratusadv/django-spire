from django_spire.ai.prompt.bots import DandyPythonPromptBot

def text_to_prompt_cli(prompt: str):
    prompt = prompt
    DandyPythonPromptBot().process(prompt)
