from __future__ import annotations


from django_spire.history.mixins import HistoryModelMixin


class OrganizationContext(HistoryModelMixin):


    class Meta:
        db_table = 'django_spire_ai_context_organization'
        verbose_name = 'Organization Context'
        verbose_name_plural = 'Organization Context'


