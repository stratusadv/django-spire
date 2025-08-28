from django_spire.knowledge.auth.controller import BaseKnowledgeAuthController


class KnowledgeAuthController(BaseKnowledgeAuthController):
    def has_tacos(self) -> bool:
        return True