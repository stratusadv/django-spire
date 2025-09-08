from django_spire.auth.controller.controller import BaseAuthController


class BaseAiChatAuthController(BaseAuthController):
    def can_delete(self):
        return self.request.user.has_perm('django_spire_ai_chat.delete_chat')
