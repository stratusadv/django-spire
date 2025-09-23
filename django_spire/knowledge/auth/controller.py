from django_spire.auth.controller.controller import BaseAuthController


class BaseKnowledgeAuthController(BaseAuthController):
    def can_access_all_collections(self):
        return self.request.user.has_perm(
            'django_spire_knowledge.can_access_all_collections'
        )

    def can_add(self):
        return self.request.user.has_perm('django_spire_knowledge.add_collection')

    def can_change(self):
        return self.request.user.has_perm('django_spire_knowledge.change_collection')

    def can_change_collection_groups(self):
        return self.request.user.has_perm(
            'django_spire_knowledge.can_change_collection_groups'
        )

    def can_delete(self):
        return self.request.user.has_perm('django_spire_knowledge.delete_collection')

    def can_view(self):
        return self.request.user.has_perm('django_spire_knowledge.view_collection')
