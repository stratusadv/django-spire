---
name: form-templates
description: Examples on how we implement our form templates (pages and cards). 
---

# Guidelines
- Use the examples as the base implementation. 
- You will have to refactor out friend and ensure the custom paths are correct.
- All django spire paths are correct.


app.friend.views.form_views.py
```python
@permission_required('friend.add_friend')
def create_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('friend.change_friend')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse|HttpResponseRedirect:
    friend = get_object_or_null_obj(models.Friend, pk=pk)

    dg.glue_model_object(request, 'friend', friend, 'view')

    if request.method == 'POST':
        form = forms.FriendForm(request.POST, instance=friend)

        if form.is_valid():
            friend, _ = friend.services.save_model_obj(**form.cleaned_data)
            add_form_activity(friend, pk, request.user)

            return redirect(
                request.GET.get(
                    'return_url',
                    reverse('mort:friend:page:list')
                )
            )

        show_form_errors(request, form)
    else:
        form = forms.FriendForm(instance=friend)

    return portal_views.form_view(
        request,
        form=form,
        obj=friend,
        template='friend/page/form_page.html'
    )

```

app.friend.forms.py
```python
class FriendForm(forms.ModelForm):

    class Meta:
        model = models.Friend
        exclude: ClassVar = []

```

This is a common form pattern to follow.
```python
@permission_required('friend.change_friend')
def ai_chat_form_view(request: WSGIRequest) -> TemplateResponse | HttpResponseRedirect:
    if request.method == 'POST':
        form = forms.AIChatForm(request.POST)

        if form.is_valid():
            ChinWaggle.services.factory.bulk_add(waggles=form.cleaned_data['waggles'])

            url = reverse('home:dashboard')
            return redirect(url)
        else:
            show_form_errors(form)

    form = forms.AIChatForm(request.POST)
    context_data = {'form': form}

    return TemplateResponse(
        request,
        context=context_data,
        template='friend/page/ai_chat_form_page.html',
    )

```