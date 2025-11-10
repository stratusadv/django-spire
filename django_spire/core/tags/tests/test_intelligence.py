from unittest import TestCase

from django_spire.core.tags.intelligence.tag_set_bot import TagSetBot

TEST_INPUT = """
    I love reading books about science fiction, fantasy, and adventure, especially ones
    that feature artificial intelligence, machine learning, and natural language processing.
    Some of my favorite authors include Isaac Asimov, J.R.R. Tolkien, and Neil Gaiman.
    I'm also interested in learning more about data science, programming languages like Python
    and Java, and emerging technologies like blockchain and the Internet of Things (IoT).
    Can you recommend some books or resources that align with these interests?
    """


class TestTagIntelligence(TestCase):
    def setUp(self):
        pass

    def test_tag_set_bot(self):
        tag_set = TagSetBot().process(TEST_INPUT)

        print(tag_set)

        self.assertIn('science', tag_set)
        self.assertIn('ai', tag_set)
        self.assertIn('fantasy', tag_set)

        self.assertNotIn('camping', tag_set)
        self.assertNotIn('art', tag_set)
        self.assertNotIn('hate', tag_set)
