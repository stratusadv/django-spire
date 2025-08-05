import django_glue as dg
from django.contrib.auth.decorators import login_required

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.form.utils import show_form_errors
from django_spire.contrib.generic_views import portal_views
from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.forms import EntryForm


@login_required()
def form_view(
        request: WSGIRequest,
        collection_pk: int,
        pk: int = 0,
) -> TemplateResponse | HttpResponseRedirect:
    entry = get_object_or_null_obj(Entry, pk=pk)
    collection = Collection.objects.get(pk=collection_pk)

    dg.glue_model_object(request, 'entry', entry, fields=['name'])

    if request.method == 'POST':
        form = EntryForm(request.POST, instance=entry)

        if form.is_valid():
            form.cleaned_data['collection'] = collection
            _ = entry.services.save_model_obj(author=request.user, **form.cleaned_data)

            return HttpResponseRedirect(
                reverse(
                    'django_spire:knowledge:collection:page:detail',
                    kwargs={'pk': collection.pk}
                )
            )

        show_form_errors(request, form)
    else:
        form = EntryForm(instance=entry)

    return portal_views.form_view(
        request,
        form=form,
        obj=entry,
        context_data={
            'entry': entry,
            'action_url': (
                reverse(
                    'django_spire:knowledge:entry:form:create',
                    kwargs={'collection_pk': collection_pk}
                )
                if pk == 0
                else reverse(
                    'django_spire:knowledge:entry:form:update',
                    kwargs={'pk': pk, 'collection_pk': collection_pk}
                )
            )
        },
        template='django_spire/knowledge/entry/page/form_page.html'
    )
