from django_spire.auth.group.decorators import permission_required


class ViewPermissionController:
    url_permissions_map = {}
    permissions_required_decorator = permission_required