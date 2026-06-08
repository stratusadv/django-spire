def form_action_name(has_pk: bool) -> str:
    return 'Edit' if has_pk else 'Create'
