from __future__ import annotations

from django_spire.ai.prompt.system import bots
from django_spire.ai.prompt.system.intel import SystemPromptIntel, SystemPromptResultIntel
from django_spire.core.tests.test_cases import BaseTestCase


class PromptBotTestCase(BaseTestCase):
    def test_role_system_prompt_bot(self) -> None:
        ISSUE_PROMPT = (
            'I am using jira to plan developer workloads And I want to be able to build very clear issues that '
            'developers will be able to read understand and take action on to complete the goal. '
            'I will give you details about a software development task that we have to achieve and I want you '
            'to return a short one sentence summary that the developer can read and understand the scope of the issue '
            'before they get into the details of it '
        )

        role_bot = bots.RoleSystemPromptBot()
        role_result = role_bot.process(ISSUE_PROMPT)

        assert role_result is not None
        assert role_result.result is not None
        assert len(role_result.result) > 0

    def test_task_system_prompt_bot(self) -> None:
        ISSUE_PROMPT = (
            'I am using jira to plan developer workloads And I want to be able to build very clear issues that '
            'developers will be able to read understand and take action on to complete the goal.'
        )

        task_bot = bots.TaskSystemPromptBot()
        task_result = task_bot.process(ISSUE_PROMPT)

        assert task_result is not None
        assert task_result.result is not None
        assert len(task_result.result) > 0

    def test_guidelines_system_prompt_bot(self) -> None:
        ISSUE_PROMPT = (
            'I want to create a system that helps users write better emails.'
        )

        guidelines_bot = bots.GuidelinesSystemPromptBot()
        guidelines_result = guidelines_bot.process(ISSUE_PROMPT)

        assert guidelines_result is not None
        assert guidelines_result.result is not None
        assert len(guidelines_result.result) > 0

    def test_output_format_system_prompt_bot(self) -> None:
        ISSUE_PROMPT = (
            'I want to create a system that returns a summary of a document.'
        )

        output_format_bot = bots.OutputFormatSystemPromptBot()
        output_format_result = output_format_bot.process(ISSUE_PROMPT)

        assert output_format_result is not None
        assert output_format_result.result is not None

    def test_system_prompt_bot_full_workflow(self) -> None:
        ISSUE_PROMPT = (
            'I am using jira to plan developer workloads And I want to be able to build very clear issues that '
            'developers will be able to read understand and take action on to complete the goal. '
            'I will give you details about a software development task that we have to achieve and I want you '
            'to return a short one sentence summary that the developer can read and understand the scope of the issue '
            'before they get into the details of it '
        )

        role_bot = bots.RoleSystemPromptBot()
        role_result = role_bot.process(ISSUE_PROMPT)
        assert role_result is not None

        task_bot = bots.TaskSystemPromptBot()
        task_result = task_bot.process(ISSUE_PROMPT)
        assert task_result is not None

        guidelines_bot = bots.GuidelinesSystemPromptBot()
        guidelines_result = guidelines_bot.process(ISSUE_PROMPT)
        assert guidelines_result is not None

        output_format_bot = bots.OutputFormatSystemPromptBot()
        output_format_result = output_format_bot.process(ISSUE_PROMPT)
        assert output_format_result is not None


class SystemPromptIntelTestCase(BaseTestCase):
    def test_system_prompt_intel_to_string(self) -> None:
        intel = SystemPromptIntel(
            role='Test Role',
            task='Test Task',
            guidelines='Test Guidelines',
            output_format='Test Output Format'
        )

        result = intel.to_string()

        assert 'Role: Test Role' in result
        assert 'Task: Test Task' in result
        assert 'Guidelines: Test Guidelines' in result
        assert 'Output Format: Test Output Format' in result

    def test_system_prompt_intel_to_string_without_output_format(self) -> None:
        intel = SystemPromptIntel(
            role='Test Role',
            task='Test Task',
            guidelines='Test Guidelines',
            output_format=None
        )

        result = intel.to_string()

        assert 'Role: Test Role' in result
        assert 'Task: Test Task' in result
        assert 'Guidelines: Test Guidelines' in result
        assert 'Output Format' not in result

    def test_system_prompt_result_intel(self) -> None:
        intel = SystemPromptResultIntel(result='Test result')

        assert intel.result == 'Test result'
