from django.contrib import messages

def show_form_errors(request, *forms):
    for form in forms:
        for field_name, error_list in form.errors.items():
            for error in error_list.data:
                error_message = f'{field_name.title()}: {" ".join(error.messages)}'
                messages.error(request, error_message)
