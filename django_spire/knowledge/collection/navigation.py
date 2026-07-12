from django_spire.knowledge.navigation import KnowledgeNavigation


class CollectionNavigation(KnowledgeNavigation):
    def __init__(self) -> None:
        super().__init__()
        self.breadcrumbs.add('Knowledge', 'django_spire:knowledge:page:home')
