from django_spire.auth.controller.controller import BaseAuthController


class BaseKnowledgeAuthController(BaseAuthController):
    def has_tacos(self) -> bool:
        return False
