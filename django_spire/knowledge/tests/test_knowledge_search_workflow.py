from __future__ import annotations

from unittest.mock import patch

from django.test import RequestFactory

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection
from django_spire.knowledge.entry.tests.factories import create_test_entry
from django_spire.knowledge.entry.version.choices import EntryVersionStatusChoices
from django_spire.knowledge.entry.version.tests.factories import create_test_entry_version
from django_spire.knowledge.intelligence.bots.knowledge_answer_bot import KnowledgeAnswerBot
from django_spire.knowledge.intelligence.bots.knowledge_entries_bot import KnowledgeEntriesBot
from django_spire.knowledge.intelligence.intel.answer_intel import AnswerIntel
from django_spire.knowledge.intelligence.intel.entry_intel import EntriesIntel, EntryIntel
from django_spire.knowledge.intelligence.intel.message_intel import KnowledgeMessageIntel
from django_spire.knowledge.intelligence.workflows.knowledge_workflow import (
    knowledge_search_workflow,
)


class KnowledgeSearchWorkflowTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.super_user

        self.collection = create_test_collection(name='Documentation')
        self.entry = create_test_entry(collection=self.collection, name='Django Setup Guide')
        self.entry_version = create_test_entry_version(entry=self.entry)
        self.entry_version.status = EntryVersionStatusChoices.PUBLISHED
        self.entry_version.save()
        self.entry.current_version = self.entry_version
        self.entry.save()

    def _process_to_future(self, intel):
        mock_future = type('MockFuture', (), {})()
        mock_future.result = intel
        return mock_future

    @patch.object(KnowledgeAnswerBot, 'process_to_future')
    @patch.object(KnowledgeEntriesBot, 'process_to_future')
    def test_knowledge_search_workflow_returns_knowledge_message_intel(
        self, mock_entries_bot, mock_answer_bot
    ) -> None:
        answer_intel = AnswerIntel(answer='Install with pip.', is_knowledge_based=True)
        entries_intel = EntriesIntel(
            entry_intel_list=[EntryIntel(relevant_heading_text='Django Setup', relevant_block_id=1)]
        )

        mock_answer_bot.return_value = self._process_to_future(answer_intel)
        mock_entries_bot.return_value = self._process_to_future(entries_intel)

        result = knowledge_search_workflow(
            request=self.request, user_input='Django setup', use_llm_preprocessing=False
        )

        assert isinstance(result, KnowledgeMessageIntel)
        assert result.answer_intel.answer == 'Install with pip.'
        assert result.answer_intel.is_knowledge_based
        assert result.entries_intel.entry_intel_list[0].relevant_heading_text == 'Django Setup'

    @patch.object(KnowledgeAnswerBot, 'process_to_future')
    @patch.object(KnowledgeEntriesBot, 'process_to_future')
    def test_knowledge_search_workflow_returns_default_message_intel_for_not_knowledge_based(
        self, mock_entries_bot, mock_answer_bot
    ) -> None:
        answer_intel = AnswerIntel(answer='Hello there!', is_knowledge_based=False)
        entries_intel = EntriesIntel(entry_intel_list=[])

        mock_answer_bot.return_value = self._process_to_future(answer_intel)
        mock_entries_bot.return_value = self._process_to_future(entries_intel)

        result = knowledge_search_workflow(
            request=self.request, user_input='Hello Django', use_llm_preprocessing=False
        )

        assert isinstance(result, KnowledgeMessageIntel) is False
        assert result.render_to_str() == 'Hello there!'

    @patch.object(KnowledgeAnswerBot, 'process_to_future')
    @patch.object(KnowledgeEntriesBot, 'process_to_future')
    def test_knowledge_search_workflow_returns_default_message_intel_when_no_entries(
        self, mock_entries_bot, mock_answer_bot
    ) -> None:
        result = knowledge_search_workflow(
            request=self.request, user_input='nonexistent term', use_llm_preprocessing=False
        )

        assert isinstance(result, KnowledgeMessageIntel) is False
        assert 'could not find' in result.render_to_str()
        mock_answer_bot.assert_not_called()
        mock_entries_bot.assert_not_called()
