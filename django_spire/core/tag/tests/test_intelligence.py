from __future__ import annotations

from unittest import TestCase

from django_spire.core.tag.intelligence.tag_set_bot import TagSetBot


TEST_INPUT = """
    I love reading books about science fiction, fantasy, and adventure, especially ones
    that feature artificial intelligence, machine learning, and natural language processing.
    Some of my favorite authors include Isaac Asimov, J.R.R. Tolkien, and Neil Gaiman.
    I'm also interested in learning more about data science, programming languages like Python
    and Java, and emerging technologies like blockchain and the Internet of Things (IoT).
    Can you recommend some books or resources that align with these interests?
    """


class TestTagIntelligence(TestCase):
    def test_tag_set_bot(self):
        tag_set = TagSetBot().process(TEST_INPUT)

        assert 'science' in tag_set
        assert 'artificial' in tag_set
        assert 'fantasy' in tag_set

        assert 'camping' not in tag_set
        assert 'art' not in tag_set
        assert 'hate' not in tag_set
