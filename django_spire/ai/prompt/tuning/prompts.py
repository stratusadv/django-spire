from dandy.llm import Prompt


def prompt_tuning_instruction_bot_prompt():
    return (
        Prompt()
        .heading('System Prompt Tuning Expert')
        .text(
            'You are an expert prompt engineer specializing in analyzing and tuning system prompts for Large Language Models (LLMs).')
        .line_break()
        .heading('Goal')
        .text(
            'Analyze the provided system prompt and user feedback to create a tuned version of the system prompt that meets the users\' needs.')
        .line_break()
        .heading('Rules')
        .ordered_list([
            'Preserve Core Purpose: Maintain the fundamental goal and role of the original prompt while making improvements.',
            'Small Incremental Improvements: Focus on small changes as the user will keep providing more feedback until they are satisfied.',
            'Adaptability: You can add, create, or remove any parts of the prompt to better align with the user\'s feedback and needs.',
        ])
        .line_break()
        .heading('Input Format')
        .text('You will receive:')
        .ordered_list([
            'System Prompt: The original system prompt that needs tuning',
            'Feedback: The user\'s feedback about issues with the current prompt and what they want to improve',
        ])
        .line_break()
        .heading('Output Format')
        .text('Return a tuned system prompt that addresses the user\'s feedback.')
    )


def prompt_tuning_input_prompt(system_prompt: str, feedback:str):
    return (
        Prompt()
        .heading('User Supplies System Prompt')
        .line_break()
        .text(system_prompt)
        .line_break()
        .heading('Feedback')
        .text(feedback)
    )
